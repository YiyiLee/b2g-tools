'''which' python2.7 > /dev/null && exec python2.7 "$0" "$@" || exec python "$0" "$@"
'''

from optparse import OptionParser
#import git
from git import *
import os
import commands

GECKO_PATH_KEY = "GECKO_PATH"
GECKO_OBJ_PATH_KEY = "GECKO_OBJDIR"

def tryBuild(options, git):
  cmd = "cd %s && %s/build.sh gecko" % (options.dir, options.dir)
  # output = os.popen(cmd)
  (status, output) = commands.getstatusoutput(cmd)

  if status != 0:
    print output

  return status

def readData(filePath):
  with open(filePath) as f:
    data = f.read().splitlines()

  return data


def retrieveValueFromKey(data, key):
  found = False

  for line in data:
    if line.startswith(key):
      value = line.split('=');
      found = True

  if found == True:
    return value[1]
  else:
    return None

def getSettingsFromConfig(dir):
  config_path = "%s/.config" % dir
  userconfig_path = "%s/.userconfig" % dir

  config_data = ""
  userconfig_data = ""

  if os.path.isfile(config_path):
    config_data = readData(config_path)

  if os.path.isfile(userconfig_path):
    userconfig_data = readData(userconfig_path)

  # default settings
  gecko_path = "%s/gecko" % dir
  output_path = "%s/objdir-gecko" % dir

  # get the settings from .config and .userconfig. The latter will override
  # former.
  if retrieveValueFromKey(config_data, GECKO_PATH_KEY):
    gecko_path = retrieveValueFromKey(config_data, GECKO_PATH_KEY)

  if retrieveValueFromKey(userconfig_data, GECKO_PATH_KEY):
    gecko_path = retrieveValueFromKey(userconfig_data, GECKO_PATH_KEY)

  if retrieveValueFromKey(config_data, GECKO_OBJ_PATH_KEY):
    output_path = retrieveValueFromKey(config_data, GECKO_OBJ_PATH_KEY)

  if retrieveValueFromKey(userconfig_data, GECKO_OBJ_PATH_KEY):
    output_path = retrieveValueFromKey(userconfig_data, GECKO_OBJ_PATH_KEY)

  #print "gecko path %s " % gecko_path
  #print "output path %s " % output_path
  return (gecko_path, output_path)

def main(options):
  (gecko_path, output_path) = getSettingsFromConfig(options.dir)
  repo = Repo(gecko_path)
  git = repo.git
  number = "-%d" % int(options.number)
  logs = git.log('--pretty=%H', number)
  log_list = logs.split()

  # clean the output folder first
  cleanOutputFolderCmd = 'rm -rf %s' % output_path
  # os.system(cleanOutputFolderCmd)

  # build from the last one(the oldest commit)
  for i in reversed(range(int(options.number))):
    #print log_list[i]
    git.checkout(log_list[i])
    if tryBuild(options, git) != 0:
      print "\n===============================================\n"
      print git.log('-1')
      return

if __name__ == '__main__':
  parser = OptionParser()
  parser.add_option('-d', '--dir', dest='dir', help='the directory of b2g(absolute path)')
  parser.add_option('-n', '--number', dest='number', help='number of commits to try')

  (options, args) = parser.parse_args()

  #if options.dir == None or options.out == None or options.fromRevision == None or options.toRevision == None:
    #parser.error('Either dir or out is not set')

  main(options)

