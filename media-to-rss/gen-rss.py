#!/usr/bin/env python
# encoding: utf-8
'''
gen-rss -- generate a RSS 2 feed from files in in directory.

gen-rss is a program that takes a directory hosted under your web site
and generates an RSS 2 feed for all files with a given extension(s).


@author:     Amine SEHILI
            
@copyright:  2014 Amine Sehili. All rights reserved.
            
@license:    GNU GPL v02

@contact:    amine.sehili@gmail.com
@deffield    updated: Nov 2014
'''

import sys
import os
import glob
import fnmatch
import time


from optparse import OptionParser

__all__ = []
__version__ = 0.1
__date__ = '2014-11-01'
__updated__ = '2014-11-26'

DEBUG = 0
TESTRUN = 0
PROFILE = 0


def createElement(link, title, guid = None, description="", pubDate=None, indent = "   ", extra_args=None):
    
    if guid is None:
        guid = link
  
    guid =  "{0}<guid>{1}</guid>\n".format(indent * 3, guid)
    link = "{0}<link>{1}</link>\n".format(indent * 3, link)
    title = "{0}<title>{1}</title>\n".format(indent * 3, title)
    descrption = "{0}<description>{1}</description>\n".format(indent * 3, description)
    
    if pubDate is not None:
        pubDate = "{0}<pubDate>{1}</pubDate>\n".format(indent * 3, pubDate)
    else:
        pubDate = ""
    
    extra = ""
    if extra_args is not None:
        for key,value in extra_args.items():
            extra += "{0}<{1}>{2}</{3}>\n".format(indent * 3, key, value, key)
    
    return "{0}<item>\n{1}{2}{3}{4}{5}{6}{7}</item>".format(indent * 2, guid, link, title, descrption, pubDate, extra, indent * 2)
    
    
    
    
def main(argv=None):
    '''Command line options.'''
    
    program_name = os.path.basename(sys.argv[0])
    program_version = "v0.1"
    program_build_date = "%s" % __updated__
 
    program_version_string = '%%prog %s (%s)' % (program_version, program_build_date)
    #program_usage = '''usage: spam two eggs''' # optional - will be autogenerated by optparse
    program_longdesc = '''''' # optional - give further explanation about what the program does
    #program_license = "Copyright 2014 user_name (organization_name)                                            \
    #            Licensed under the Apache License 2.0\nhttp://www.apache.org/licenses/LICENSE-2.0"
 
    if argv is None:
        argv = sys.argv[1:]
    try:
        # setup option parser
        parser = OptionParser(version=program_version_string, epilog=program_longdesc, description=program_license)
        parser.add_option("-d", "--dirname", dest="dirname", help="Directory to look for media files in. This directory name will be append to your host name to create absolute paths to your media files.", metavar="RELATIVE_PATH")
        parser.add_option("-r", "--recursive", dest="recursive", help="Look for media files recursively in sub directories ? [Default:False]", action="store_true", default=False)
        parser.add_option("-e", "--extensions", dest="extensions", help="A comma separated list of extensions (e.g. mp3,mp4,avi,ogg) [Default:None => all files]", type="string", default=None, metavar="STRING")
        
        parser.add_option("-o", "--out", dest="outfile", help="Output RSS file [default: %STDOUT]", metavar="FILE")
        parser.add_option("-H", "--host", dest="host", help="Host name (or IP address), possibly with a path to the base directory where your media directory is located\
        Examples of host names:\
           mywebsite.com/media/JapaneseLessons\n \
           mywebsite                          \n \
           myMachineName                      \n \
           192.168.1.12/media/JapaneseLessons \n \
           http://192.168.1.12/media/JapaneseLessons \n", metavar="A_WEB_SITE")
        
        
        
        parser.add_option("-t", "--title", dest="title", help="Title of the podcast [Defaule:None]", default=None, metavar="STRING")
        parser.add_option("-p", "--description", dest="description", help="Description of the [Defaule:None]", default=None, metavar="STRING")
        parser.add_option("-C", "--sort-creation", dest="sort_creation", help="Sort files by date of creation instead of name (default) and current date", action="store_true", default=False)
        
        
        
           
        
        
        parser.add_option("-v", "--verbose", dest="verbose", action="count", help="set verbosity level [default: %default]")
        
        
        # process options
        (opts, args) = parser.parse_args(argv)
        
                 
        if opts.dirname is None or opts.host is None:
            raise Exception("Usage: python %s -d directory -H hostname [-o output -r]\n   For more information run %s --help\n" % (program_name,program_name))
        
        if not os.path.isdir(opts.dirname) or not os.path.exists(opts.dirname):
            raise Exception("--direname must be a path to an existing directory")
        
        
        dirname = opts.dirname
        if dirname[-1] != os.sep:
            dirname += os.sep
        host = opts.host
        if host[-1] != '/':
            host += '/'
        
        if not host.lower().startswith("http://") and not host.lower().startswith("https://"):
            host = "http://" + host 
        
        
        title = ""
        description = ""
        link = opts.host
        if opts.outfile is not None:
            if link[-1] == '/':
                link += opts.outfile
            else:
                link += '/' + opts.outfile
        
        if opts.title is not None:
            title = opts.title
            
        if opts.description is not None:
            description = opts.description
        
        #<lastBuildDate>Sat, 07 Sep 2002 00:00:01 GMT</lastBuildDate>
        
        
        allfiles = []
        if opts.recursive:
            for root, dirnames, filenames in os.walk(dirname.encode("utf-8")):
                for name in filenames:
                    allfiles.append(os.path.join(root, name))
        else:
            allfiles = [f for f in glob.glob(dirname.encode("utf-8") + "*")\
                         if os.path.isfile(f)]
        
        
        chosenfiles = []
        if opts.extensions is not None:
            exts = ["*.{0}".format(e) for e in  opts.extensions.split(",")]
            for e in exts:
                chosenfiles += [n for n in allfiles if fnmatch.fnmatch(n.lower(), e.lower())]            
        else:
            chosenfiles = allfiles
        
        
        pubDates = []
        if opts.sort_creation:
            for f in chosenfiles:
                #pubDates += [os.path.getctime(f)]
                pubDates += time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.localtime(os.path.getctime(f)))
                
            
            sortedFiles = sorted(zip(chosenfiles, pubDates),key=lambda f: - f[1]) # '- f[1]' => sort dates so that the newest files are on top
               
        else:
            pubDates = [time.time()] * len(chosenfiles)
            sortedFiles = sorted(zip(chosenfiles, pubDates),key=lambda f: f[0]) # sort files by name
            
            
        # build items    
        items = []
        for f in sortedFiles:
            pdate = time.ctime(f[1])
            items.append(createElement(link= host + f[0], title=os.path.basename(f[0]) , guid=host + f[0], description=os.path.basename(f[0]), pubDate=pdate))
            
                    
        if opts.outfile is not None:
            outfp = open(opts.outfile,"w")
        else:
            outfp = sys.stdout
        
        outfp.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        outfp.write('<rss version="2.0">\n')
        outfp.write('   <channel>\n')
        outfp.write('      <title>{0}</title>\n'.format(title))
        outfp.write('      <description>{0}</description>\n'.format(description))
        outfp.write('      <link>{0}</link>\n'.format(link))
         
        for item in items:
            outfp.write(item + "\n")
                
        outfp.write('')
        outfp.write('   </channel>\n')
        outfp.write('</rss>\n')
        
        
        
        if outfp != sys.stdout:
            outfp.close()
        
    except Exception, e:
        sys.stderr.write(str(e) + "\n")
        #sys.stderr.write(indent + "  for help use --help\n")
        return 2


if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-h")
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'gen-rss_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    sys.exit(main())