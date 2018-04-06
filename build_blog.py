import os
import shutil
import subprocess
import sys
import tempfile
# https://zserge.com/blog.html


CSS = "resources/blog.css"

HEADER = """
<table style="margin-top: 2em; width: 100%; border: none;">
    <tr style="border: none;">
        <td style="border: none;">
            <img src="resources/JT.jpeg" style="width: 3em;"/>
        </td>
        <td style="border: none; text-align: right;">
            <span style="margin-left: 2em;">
                <a href="index.html">about</a>
            </span>
            <span style="margin-left: 2em;">
                <a href="index.html">posts</a>
            </span>
            <span style="margin-left: 2em;">
                <a href="https://github.com/pyohannes">github</a>
            </span>
        </td>
    </tr>
</table>
"""

FOOTER = """
<p style="font-size: 0.6em;">
  &copy; 2017 
  <a href="http://johannes.tax">Johannes Tax</a> 
  (<a href="mailto:johannes@johannes.tax">johannes@johannes.tax</a>)
</p>
"""


def compile_rst(rst):
    tmpdir = tempfile.mkdtemp()
    try:
        tmpfile = os.path.join(tmpdir, ".rst")
        with open(tmpfile, "w") as f:
            f.write(rst)
        p = subprocess.Popen(
            [ "rst2html", 
              "--stylesheet=html4css1.css,%s" % CSS,
              tmpfile],
            stdout=subprocess.PIPE)
        out, err = p.communicate()
        out = out.decode('utf-8')
        out = out.replace("<body>", "<body>\n%s" % HEADER)
        out = out.replace("</body>", FOOTER)
        return out
    finally:
        shutil.rmtree(tmpdir)


class BlogEntry():
    def __init__(self, title, date, source):
        self.title = title
        self.date = date
        self.source = source
        self._compiled = None

    @property
    def filename(self):
        return "%s.html" % self.title.replace(" ", "_")

    def get_source(self):
        pass

    def compile(self):
        if not self._compiled:
            src = self.get_source()
            src += "\n Posted on %s" % self.date
            self._compiled = compile_rst(src)
        return self._compiled

    def write(self, outputdir):
        fname = os.path.join(outputdir, self.filename)
        with open(fname, "w") as f:
            f.write(self.compile())
        return fname


class GitBlogEntry(BlogEntry):
    def get_source(self):
        if not hasattr(self, "_src"):
            tmpdir = tempfile.mkdtemp()
            try:
                subprocess.call(["git", "clone", self.source, tmpdir])
                with open(os.path.join(tmpdir, "README.rst"), "r") as f:
                    self._src = f.read()
            finally:
                shutil.rmtree(tmpdir)
        return self._src


def make_index_html(sources):
    rst = '''Latest Posts
============

'''
    for s in sources[:6]:
        rst += "%s ... " % s.get_source()[:300].replace("=", "-")
        rst += "`Read more <%s>`_\n\n" % s.filename

    print(rst)

    return compile_rst(rst)


SOURCES = [
        GitBlogEntry(
            title="Unit testing with Fortran and CTest",
            date="2017-04-06",
            source="git@github.com:pyohannes/ctest-fortran-unittest"),
        GitBlogEntry(
            title="Unit testing with Fortran and CTest",
            date="2017-04-06",
            source="git@github.com:pyohannes/ctest-fortran-unittest"),
]



if __name__ == '__main__':
    outputdir = sys.argv[1]
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)

    for s in SOURCES:
        s.write(outputdir)


    with open(os.path.join(outputdir, "index.html"), "w") as f:
        f.write(make_index_html(SOURCES))

    shutil.copytree('resources', os.path.join(outputdir, 'resources'))
