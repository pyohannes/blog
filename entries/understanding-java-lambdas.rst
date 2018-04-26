Understanding Java Lambdas
============================

It took me quite some reading and coding to finally understand how Java Lambdas 
actually work conceptually. Most tutorials and introductions I read follow a 
top-down approach, starting with use cases and in the end leaving conceptual 
questions open. In this post I want to offer a bottom-up explanation, deriving
the concept of Lambdas from other established Java concepts.

Firstly typing of methods is introduced, which is a prerequisite for supporting
methods as first-class citizens. Based on this the concept of Lambdas is
presented as an advancement and special case of anonymous class usage. All this
is illustrated by the implementation and usage of the |higher-order function map|_.

.. |higher-order function map| replace:: higher-order function ``map``
.. _higher-order function map: https://en.wikipedia.org/wiki/Map_(higher-order_function)

The primary audience of this post are people who grasp the basics of functional
programming and who want to understand how Lambdas fit into the Java language
conceptually.


Method types
------------

From Java 8 on methods are `first-class citizens <https://en.wikipedia.org/wiki/First-class_citizen>`__. 
Following the standard definition, a first-class citizen in a programming
language is an entity that can be

- passed as an argument,
- returned from a method and
- assigned to a variable.

In Java, every argument, return value or variable is typed, therefore every
first-class citizen has to be typed. A type in Java can be one of the following:

- a builtin type (e. g. ``int`` or ``double``)
- a class (e. g. ``ArrayList``)
- an interface (e. g. ``Iterable``)

Methods are typed via interfaces. They do not implicitely implement certain
interfaces, but, when necessary, the Java compiler implicitely checks during 
compile time  if a method conforms to an interface. An example should
illustrate this:

.. code:: java

    class LambdaMap {
        static void oneStringArgumentMethod(String arg) {
            System.out.println(arg);
        }
    }

Regarding the type of the method ``oneStringArgumentMethod`` it is of relevance
that the method is static, the return type is ``void`` and that it accepts one
argument of type ``String``. A static method conforms to an interface that
contains a method ``apply``, whose signature in turn conforms to the signature
of the static method. An interface matching the method
``oneStringArgumentMethod`` therefore must meet the following criteria:

- It must contain a method called ``apply``.
- The return type of this method must be ``void``.
- This method must accept one argument that an object of type ``String`` can be
  casted to.

Amongst the interfaces conforming to this criteria, the following one might be the most
obvious:

.. code:: java

    interface OneStringArgumentInterface {
        void apply(String arg);
    }

With the help of this interface the method can assigned to a variable:

.. code:: java

    OneStringArgumentInterface meth = LambdaMap::oneStringArgumentMethod;

Using interfaces as a types in this way, methods can thus be assigned to
variables, passed as parameters and returned from methods:

.. code:: java

    static OneStringArgumentInterface getWriter() {                             
        return LambdaMap::oneStringArgumentMethod;                              
    }                                                                           

    static void write(OneStringArgumentInterface writer, String msg) {
        writer.apply(msg);                                                      
    }  

Finally methods are first-class citizens in Java!

Generic method types
--------------------

As with collections, generics add a lot of power and flexibility to method types. 
Generic method types make it possible to implement functional algorithms 
disregarding certain type informations. This ability will be used below in the 
implementation of the ``map`` method.

A generic version of the ``OneStringArgumentInterface`` is provided here:

.. code:: java

    interface OneArgumentInterface<T> {
        void apply(T arg);
    }

The method ``oneStringArgumentMethod`` can be assigned to it:

.. code:: java

    OneArgumentInterface<String> meth = LambdaMap::oneStringArgumentMethod;

Using generic method types one can now implement algorithms in a generic way, as
one is used to from collections:

.. code:: java

    static <T> void applyArgument(OneArgumentInterface<T> meth, T arg) {
        meth.apply(arg);
    }

The method above does not do anything useful, however it can at least give a
first idea how support for methods as first-class citizens can lead to very 
concise and flexible code:

.. code:: java

    applyArgument(Lambda::oneStringArgumentMethod, "X");

Implementing ``map``
----------------------

Amongst higher-order functions, ``map`` is a classic. The first argument to 
``map`` is a function that accepts one argument and returns a value; the second
argument is a list of values. ``map`` applies the passed function to every item
of the passed list and returns a new list with the resulting values. The
following snippet from a Python session illustrates its usage very well:

.. code:: python

    >>> map(math.sqrt, [1, 4, 9, 16])
    [1.0, 2.0, 3.0, 4.0]

In the remaining part of this section a Java implementation of this function 
will be given. Java 8 already offers this functionality via streams. 
As it mainly serves educational purposes, the implementation given in this
section is kept deliberately simple and will be restricted to work on ``List``
objects only.

In Java, as opposed to Python, one first has to consider the type of the
first argument to ``map``: a method accepting one argument and returning a
return value. The argument type and the return type can be different. The
following interface fits the purpose, where obviously ``I`` denotes the type of
the argument (input) and ``O`` denotes the type of the return value (output):

.. code:: java

    interface MapFunction<I, O> {
        O apply(I in);
    }

The implementation of the generic ``map`` method itself becomes surprisingly
simple and straightforward:

.. code:: java

    static <I, O> List<O> map(MapFunction<I, O> func, List<I> input) {
        List<O> out = new ArrayList<>();

        for (I in : input) {
            out.add(func.apply(in));
        }

        return out;
    }

#. A new list ``out`` is created (holding objects of the ``O`` output type).
#. In a loop over the ``input`` list, ``func`` is applied to every item of the
   list. The return value is added to ``out``.
#. ``out`` is returned.

Here is an example of the ``map`` method in action:

.. code:: java

    MapFunction<Integer, Double> func = Math::sqrt;

    List<Double> output = map(func, Arrays.asList(1., 4., 9., 16.));
    System.out.println(output);

Motivated by the Python one-liner, this can of course be expressed in a more
concise way:

.. code:: java

    System.out.println(map(Math::sqrt, Arrays.asList(1., 4., 9., 16.)));

Well, Java is not Python after all ...

Lambdas, finally!
-----------------

The inclined reader will have noticed that there has not been any mention of a
Lambda yet. That's owing to following a bottom-up approach - however, the
foundations are almost set and Lambdas will be introduced in the following
section.

The following use case serves as a basis: having a list of doubles denoting 
circle radiuses, a list of corresponding circle areas has to be obtained. The 
``map`` method is predestined for this task. The formula for calculating the
area of a circle is well known:

.. math::

    A = r^{2} \pi

A method applying this formula is easily implemented:

.. code:: java

    static Double circleArea(Double radius) {
        return Math.sqrt(radius) * Math.PI;
    }

This method can now be used as first argument to the ``map`` method:

.. code:: java

    System.out.println(
            map(LambdaMap::circleArea, 
                Arrays.asList(1., 4., 9., 16.)));

Assuming the method ``circleArea`` is only needed this one time, it does not 
make sense to clutter the class interface with it and to separate its 
implementation from the one place where it is actually used. A Java best 
practice is to use an anonymous class in this case. As one can see, this works 
out well with instantiating an anonymous class that implements the 
``MapFunction`` interface:

.. code:: java

    System.out.println(
            map(new MapFunction<Double, Double>() {                                 
                    public Double apply(Double radius) {                            
                        return Math.sqrt(radius) * Math.PI;                         
                    }                                                               
                },                                                                  
                Arrays.asList(1., 2., 3., 4.)));

That's looks nifty, however many will consider the functionally equivalent
solution below clearer and more readable:

.. code:: java

    List<Double> out = new ArrayList<>();                                   
    for (Double radius : Arrays.asList(1., 2., 3., 4.)) {                   
        out.add(Math.sqrt(radius) * Math.PI);                               
    }                                                                       
    System.out.println(out);

Having come thus far, it is finally time use a Lambda expression. The reader
should notice how the Lambda can replace the anonymous class presented above:

.. code:: java

    System.out.println(                                                     
            map(radius -> { return Math.sqrt(radius) * Math.PI; },          
                Arrays.asList(1., 2., 3., 4.)));

That looks concise and clear - note how the Lambda expression lacks any
explicit type information. No explicit template instantiation, no method signatures.

A Lambda expression consists of two parts, which are separated by a ``->``. The
first part denotes an argument list, the second part contains the actual
implementation. 

The Lambda expression serves the exact same purpose as the anonymous class, 
however it gets rid of lots of boilerplate code that the compiler can infer 
automatically anyway. Let's compare the two approaches once again and then
analyze, what work the compiler takes off the developer's back.

.. code:: java

    MapFunction<Double, Double> functionLambda =                            
            radius -> Math.sqrt(radius) * Math.PI;                          

    MapFunction<Double, Double> functionClass =                             
            new MapFunction<Double, Double>() {                             
                public Double apply(Double radius) {                        
                    return Math.sqrt(radius) * Math.PI;                     
                }                                                           
            };  

- For a Lambda implementation that consists of only one expression, the return
  statement and the curly braces can be omitted. This makes it even shorter.
- The return type of the Lambda expression is infered from the Lambda
  implementation.
- I am not completely sure about the argument types, but I think those must be
  infered from the context the Lambda expression is used in.
- Finally the compiler has to check if the return type matches the context the
  Lambda is used in and if the argument types match the Lambda implementation.

This all can be done during compile time, there is no runtime overhead at all.

Conclusion
----------

All in all, the concept of Lambdas in Java is neat. I allows for more concise
and clearer code and reliefs the programmer from writing boilerplate code that
can be infered by the compiler anyway. It's syntactic sugar, as shown above it's 
nothing that cannot also be achieved by using anonymous classes. However, I
would say it is very sweet syntactic sugar.

On the other hand, Lambdas also allow for code that is much more obfuscated and
harder to debug. The Python community realized this long ago - although Python
has Lambdas too, it is generally considered bad style to use them extensively
(it is not hard to avoid them when nested functions can be used). For Java I
would give similar advice. Without doubt there are situations in which the use
of Lambdas can lead to significantly shorter and more readable code, mostly in 
connection with streams. In other
situations one is most likely better off if one resorts to more conservative
approaches and best practices.

Links
-----

- The `official documentation <https://docs.oracle.com/javase/tutorial/java/javaOO/lambdaexpressions.html>`__ for Java Lambdas.
- The package `java.util.function <https://docs.oracle.com/javase/8/docs/api/java/util/function/package-summary.html>`__ contains lots of different Lambda interfaces
  and reliefs the programmer from introducing own interfaces like it was done with
  ``MapFunction`` above.
- `This post <https://www.codementor.io/eh3rrera/using-java-8-method-reference-du10866vx>`__ describes how to use Lambdas for other method types like
  instance methods or constructors.
