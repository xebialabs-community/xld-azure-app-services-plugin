import ftplib
import sys
import os

print "Connecting to FTP host %s as %s" % (deployed.container.ftpHostname, deployed.container.ftpDeploymentUsername)
ftp = ftplib.FTP(deployed.container.ftpHostname, deployed.container.ftpDeploymentUsername, deployed.container.ftpDeploymentPassword)

try:
    for dirpath, dirnames, filenames in os.walk(deployed.file.path):
        if dirpath.startswith(deployed.file.path):
            relpath = dirpath[len(deployed.file.path) + 1:]
            targetpath = deployed.physicalPath + '/' + relpath

            print "Changing working directory to %s" % (targetpath)
            ftp.cwd(targetpath)

            for filename in filenames:
                print "Uploading %s" % (filename)
                with open(os.path.join(dirpath, filename), 'r') as f:
                    ftp.storbinary('STOR ' + filename, f)

            for dirname in dirnames:
                print "Creating directory %s" % (dirname)
                ftp.mkd(dirname)

        else:
            print "%s is not in %s" % (dirpath, deployed.file.path)
finally:
    print "Closing FTP connection"
    ftp.quit()
