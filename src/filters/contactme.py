
#<iframe src="http://contactme.com/50b7866496f35100020230ea/embed" frameborder="0" scrolling="no" allowtransparency="true" style="height: 500px; width: 510px;"></iframe>
class CustomFilter(object):

    name = 'contactme'
    description = 'Embeds a ContactMe.com form'
    author = 'Aaron Meier'
    version = '1.0'
    usage = '[[contactme|formid|<width>|<height>]]'
    pattern = '\[\[\s?contactme\|(.*?)\]\]'
    filetype_support = ['html', 'md', 'rst','textile']

    def __init__(self, ut, pb):
        self.pb = pb
        self.ut = ut

    def pre_filter(self, match):
        args = [a.strip() for a in match.split('|')]

        form_id = args[0]
        width = '510px'
        height = '500px'

        if len(args) > 1 and args[1] != '':
            width = args[1]
        if len(args) > 2 and args[2] != '':
            height = args[2]

        html = '<iframe src="http://contactme.com/%(form_id)s/embed"'\
               ' frameborder="0" scrolling="no" allowtransparency="true"'\
               ' style="height: %(height)s; width: %(width)s;">'\
               '</iframe>'\
               %({'form_id':form_id, 'height':height, 'width':width})

        if self.pb['filetype'] == 'rst':
            html = '\n.. raw:: html\n\n\t%s\n'%(html)
        elif self.pb['filetype'] == 'textile':
            html = 'notextile.. %s\n'%(html)

        return html

    def post_filter(self, match):
        return match
