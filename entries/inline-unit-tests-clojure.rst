Inline unit tests in Clojure
============================

I'm a fan of inline unit testing. I firstly encountered the idea with
Rust and I got hooked on it when applying it in Racket.
This post is about sharing my experiences with using inline unit testing in
Clojure. Step-by-step I will show how I set up a Clojure project with inline
unit tests, while doing that I will highlight the obstacles I encountered and
explain how I resolved them.

An empty Clojure project created with Leiningen serves as a starting point:

.. code::

    $ lein new app inline-tests                                                       
    $ cd inline-tests
    $ rm -r src/inline_tests/core.clj test

In this project the function ``round5`` will be implemented and tested. To
illustrate the use of tests as documentation, I chose an algorithm that is not
completely trivial and obvious. The function takes an integer as input and
rounds it off according to the following rules:

 - The input is rounded off to the closest positive multiple of 5.
 - Negative inputs round off to 0.
 - 0 is considered a positive number, but not a multiple of 5.

Based on this informal specification, the possible inputs are partitioned
using equivalence partitioning to aid the test design: 

+-------------------------+------------------------------------------+
| :math:`i < 0`           | Negative numbers (rounded off to 0).     |
+-------------------------+------------------------------------------+
| :math:`0 \leq i \leq 7` | Positive numbers rounded off to 5.       |
+-------------------------+------------------------------------------+
| :math:`i > 8`           | Positive numbers not rounded off to 5.   |
+-------------------------+------------------------------------------+

``deftest``
-----------

The file ``src/inline_tests/round5.clj`` defining the namespace 
``inline_tests.round5`` will hold the implementation of the function ``round5``
as well as the related unit tests:

.. code:: clojure

    (ns inline_tests.round5
     (:require [clojure.test :refer [deftest is testing]]))
    
The ``clojure.test`` test framework shipped with Clojure is well designed,
powerful and yet straightforward to use. I use ``deftest`` to define a unit test,
``is`` to test assertions and ``testing`` to group assertions. The following test
is defined using these three functions and considers input from all 
equivalence partitions:

.. code:: clojure

    (deftest round5-test
      (let [roundsto (fn [e] #(= e (round5 %)))]
        (testing "Negative numbers"
          (is (every? (roundsto 0) (range -20 0))))
        (testing "Positive numbers rounding to 5"
          (is (every? (roundsto 5) (range 0 8))))
        (testing "Positive numbers rounding not to 5"
          (is (every? (roundsto 10) (range 8 13)))
          (is (every? (roundsto 20) (range 18 23)))
          (is (= 1020 (round5 1022))))))

Emphasis is placed on providing readable assertions. The expression

.. code:: clojure

    (is (every? (roundsto 5) (range 0 8)))

can be read as 

    *assert that integers between 0 and 8 (not including 8) rounds off to 5*. 
    
Used like this, unit tests can be used to illustrate the purpose and 
functionality of a function and thus explanatory documentation or comments 
can be omitted.

The actual implementation of the ``round5`` function directly follows the 
corresponding unit test and is given without further explanation.

.. code:: clojure

    (defn round5
      "Round to the closest positive multiple of 5.
      Negative numbers round to 0, which is not 
      considered a multiple of 5."
      [n]
      (cond (< n 0)
            0
            (< n 8)
            5
            :else
            (let [remainder (rem n 5)
                  quotient (quot n 5)]
              (* 5 (+ quotient
                      (if (<= remainder 2)
                          0
                          1))))))

``:test-paths``
---------------

So far this almost exactly corresponds to the way it worked in Racket. There I
just ran ``raco test``, which collected all tests in a ``test`` namespace anywhere
in the project and ran them. Trying the equivalent ``lein test`` I get the
following output:

.. code::
 
    $ lein test

    lein test user

    Ran 0 tests containing 0 assertions.
    0 failures, 0 errors.

No tests are found. The test is run correctly when the full namespace
``inline_tests.round5`` is given as argument to  ``lein test``, however, that is
too cumbersome. Furthermore I used ``lein test`` in other projects and it worked
as expected. Finally things got clear to me when I digged into the Leiningen
source code.

Leiningen tries to collect tests from all namespaces defined in files below
paths that are defined in the ``:test-paths`` option of Leiningen projects. By
default, this option is initialized with ``["test"]`` and thus tests are
collected only from namespaces defined in the ``test`` directory. This taught me
two things:

#. Leiningen with its default configuration does not support inline unit
   tests.
#. The Leiningen source contains a sample ``project.clj`` file with an annotated 
   reference of all options that are supported. I can only recommend going
   through this file. Digging into the Leiningen source code was instructive,
   but unnecessary.

I extended the ``project.clj`` by the option ``:test-paths ["src" "test"]``, as I
intend to keep unit test inline but place integration tests separately into the
``test`` subfolder.


``declare``
-----------

That still was not the whole story. Running ``lein test`` now fails with a
``RuntimeException`` giving the message:

.. code::

    Unable to resolve symbol: round5 in this context, 

The unit test is found and executed, however the ``round5`` function is not. The
cause for this error is trivial: in Clojure, like in Java or C, every symbol
has to be defined before it is used. Spoiled by Racket and Python,
where functions can reference global variables before they are assigned, this
was not immediately obvious to me. Fortunately there is a simple solution for
this trivial problem: symbols can be declared beforehand via the function
``declare``. Adding the line ``(declare round5)`` before the definition of the
``round5-test`` unit test does the trick and the test can be run successfully:

.. code:: 

    $ lein test

    lein test inline_tests.round5

    Ran 1 tests containing 5 assertions.
    0 failures, 0 errors.


Readability
-----------

One of the biggest concerns regarding inline unit tests is readability - the
fear that productive code gets lost in test code. To address this concern, let 
me show you how my editor of choice ``vim`` displays the file 
``src/inline_tests/round5.clj``:

.. code:: 

    (ns inline_tests.round5                                                         
      (:require [clojure.test :refer [deftest is testing]]))                                 
    
    (declare round5)                                                                
    
    (deftest round5-test                                                            
    +--  9 lines: (let [expected (fn [e] #(= e (round5 %)))]----------
    
    (defn round5                                                                    
    +-- 15 lines: "Round to the closest positive multiple of 5."------

The point I want to make here is that a well configured editor can
substantially enhance the readability of source files, so that the inclusion of
unit tests (be it done in a sane and consistent style) has no negative effect
on it.
