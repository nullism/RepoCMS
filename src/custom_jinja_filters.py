from jinja2 import contextfilter, environmentfilter, evalcontextfilter, Markup
import time


def timestamp(epoch, eformat='%Y-%m-%d %H:%M'):
    return time.strftime(eformat, time.localtime(epoch))    

def timedelta(epoch, dformat='%dd, %Hh, %Mm, %ss ago'):
    delta = int(time.time() - epoch)    
    secs = delta % 60
    mins = (delta / 60) % 60
    hours = (delta / 60 / 60) % 24
    days = (delta / 60 / 60 / 24)
    dformat = dformat.replace('%d',str(days))
    dformat = dformat.replace('%M',str(mins))
    dformat = dformat.replace('%H',str(hours))
    dformat = dformat.replace('%s',str(secs))
    
    return dformat
