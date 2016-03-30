import ftplib
import sys
import os

print "Connecting to FTP host %s as %s" % (previousDeployed.container.ftpHostname, previousDeployed.container.ftpDeploymentUsername)
ftp = ftplib.FTP(previousDeployed.container.ftpHostname, previousDeployed.container.ftpDeploymentUsername, previousDeployed.container.ftpDeploymentPassword)

try:
    for dirpath, dirnames, filenames in os.walk(previousDeployed.file.path, topdown=False):
        if dirpath.startswith(previousDeployed.file.path):
            relpath = dirpath[len(previousDeployed.file.path) + 1:]
            targetpath = previousDeployed.physicalPath + '/' + relpath

            print "Changing working directory to %s" % (targetpath)
            ftp.cwd(targetpath)

            for filename in filenames:
                print "Deleting file %s" % (filename)
                ftp.delete(filename)

            for dirname in dirnames:
                print "Removing directory %s" % (dirname)
                ftp.rmd(dirname)

        else:
            print "%s is not in %s" % (dirpath, previousDeployed.file.path)
finally:
    print "Closing FTP connection"
    ftp.quit()
