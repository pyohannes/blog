import os
import shutil
import subprocess
import sys
import tempfile
# https://zserge.com/blog.html


CSS = "resources/blog.css"

ICON = '<link rel="icon" href="resources/JT.jpeg"/>'

HEADER = """
<table style="margin-top: 2em; width: 100%; border: none;">
    <tr style="border: none;">
        <td style="border: none;">
            <img src="resources/JT.jpeg" style="width: 3em;"/>
        </td>
        <td style="border: none; text-align: right;">
            <span style="margin-left: 2em;">
                <a href="index.html">posts</a>
            </span>
            <span style="margin-left: 2em;">
                <a href="https://github.com/pyohannes">github</a>
            </span>
            <span style="margin-left: 2em;">
                <a href="mailto:johannes@johannes.tax">email</a>
            </span>
        </td>
    </tr>
</table>
"""

FOOTER = """
<p style="font-size: 0.6em;">
  &copy; 2018 
  <a href="http://johannes.tax">Johannes Tax</a> 
  (<a href="mailto:johannes@johannes.tax">johannes@johannes.tax</a>)
</p>
"""

DISQUS = """
<div id="disqus_thread"></div>
<script>

/**
*  RECOMMENDED CONFIGURATION VARIABLES: EDIT AND UNCOMMENT THE SECTION BELOW TO INSERT DYNAMIC VALUES FROM YOUR PLATFORM OR CMS.
*  LEARN WHY DEFINING THESE VARIABLES IS IMPORTANT: https://disqus.com/admin/universalcode/#configuration-variables*/
var disqus_config = function () {
this.page.url = '%s';  // Replace PAGE_URL with your page's canonical URL variable
this.page.identifier = '%s'; // Replace PAGE_IDENTIFIER with your page's unique identifier variable
};
(function() { // DON'T EDIT BELOW THIS LINE
var d = document, s = d.createElement('script');
s.src = 'https://johannes-tax.disqus.com/embed.js';
s.setAttribute('data-timestamp', +new Date());
(d.head || d.body).appendChild(s);
})();
</script>
<noscript>Please enable JavaScript to view the <a href="https://disqus.com/?ref_noscript">comments powered by Disqus.</a></noscript>
"""                            


def compile_rst(rst, comments_id=None):
    tmpdir = tempfile.mkdtemp()
    try:
        tmpfile = os.path.join(tmpdir, ".rst")
        with open(tmpfile, "w") as f:
            f.write(rst)
            if comments_id:
                f.write("\n\nComments\n--------\n\n")
        p = subprocess.Popen(
            [ "rst2html", 
              "--stylesheet=html4css1.css,%s" % CSS,
              tmpfile],
            stdout=subprocess.PIPE)
        out, err = p.communicate()
        out = out.decode('utf-8')
        out = out.replace("<head>", "<head>\n%s" % ICON)
        out = out.replace("<body>", "<body>\n%s" % HEADER)
        if comments_id:
            commentfooter = DISQUS % ("http://johannes.tax/%s" % comments_id,
                                      comments_id)
            out = out.replace("</body>", "%s</body>" % commentfooter)
        out = out.replace("</body>", "%s</body>" % FOOTER)
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
        src = self.read()
        lines = src.split('\n')
        lines.insert(2, "\nPosted on %s\n" % self.date)
        return '\n'.join(lines)

    def compile(self):
        if not self._compiled:
            src = self.get_source()
            self._compiled = compile_rst(src, comments_id=self.filename)
        return self._compiled

    def write(self, outputdir):
        fname = os.path.join(outputdir, self.filename)
        with open(fname, "w") as f:
            f.write(self.compile())
        return fname


class TextBlogEntry(BlogEntry):
    def read(self):
        with open(self.source) as f:
            return f.read()


class GitBlogEntry(BlogEntry):
    def read(self):
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
        snippet = s.get_source()[:300].replace('=', '-')
        lines = snippet.split('\n')
        lines[0] = '`%s <%s>`_' % (lines[0], s.filename)
        lines[1] = '-' * len(lines[0])
        rst += "%s ... " % '\n'.join(lines)
        rst += "`Read more <%s>`__\n\n" % s.filename

    print(rst)

    return compile_rst(rst)


SOURCES = [
        TextBlogEntry(
            title="Understanding Java Lambdas",
            date="2017-04-25",
            source="entries/understanding-java-lambdas.rst"),
        GitBlogEntry(
            title="Unit testing with Fortran and CTest",
            date="2017-04-06",
            source="git@github.com:pyohannes/ctest-fortran-unittest"),
#        TextBlogEntry(
#            title="Don't require a minimum code coverage",
#            date="2017-03-29",
#            source="entries/no-minimum-coverage.rst"),
        TextBlogEntry(
            title="Letter spacing for headlines in LaTeX",
            date="2017-03-25",
            source="entries/latex-letter-spacing.rst")
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
