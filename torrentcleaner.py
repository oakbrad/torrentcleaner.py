#!/usr/bin/python
#
# Transmission RPC Reference
# http://pythonhosted.org/transmissionrpc/reference/transmissionrpc.html
# Command spec:
# https://trac.transmissionbt.com/browser/trunk/extras/rpc-spec.txt
#
# transmission-fluid
# http://pythonhosted.org/transmission-fluid/


#
# Script pulls list of torrents
# Apollo/Waffles torrents in the downloads/complete/torrents folder
# Get filed to seeds/apollo or seeds/waffles
# Also copied to to_process (for headphones?)
#
# Ru torrents are seeded to 1:1 and then removed + delete files
#
# Public torrents are removed and left in downloads/complete/torrents
#

from transmission import Transmission
import shutil
import os

#
# Connect and retrieve torrents
#
client = Transmission(host='localhost',username='root',password='XXXXX')
response = client('torrent-get',fields=['id','name','percentDone','seedRatioMode','uploadRatio','downloadDir','trackers'])

doneTorrents = 0;
moveTorrents = 0;
removeTorrents = 0;
ruDeleted = 0;
ruSeeding = 0;
totalTorrents = len(response['torrents'])


loop = 0;
print "Connecting to Transmission to check torrents..."
while (loop < totalTorrents):
    currentTorrent = response['torrents'][loop];

    # DO THIS FOR ALL DONE TORRENTS
    if (currentTorrent['percentDone'] == 1):
        doneTorrents = doneTorrents + 1;

        #
        # SORT TORRENTS BY TRACKER
        #

        # APOLLO
        # ACTION: put in seeds/apollo, copy to to_process
        if "apollo" in currentTorrent['trackers'][0]['announce']:
            # If it's in the download folder...
            if "/mnt/usb1/downloads/complete/torrents" in currentTorrent['downloadDir']:
                torrentSource =  currentTorrent['downloadDir'] + "/" + currentTorrent['name']
                torrentprocessDestination = "/mnt/usb1/to_process/" + currentTorrent['name']
                torrentseedDestination = "/mnt/usb1/seeds/apollo/" + currentTorrent['name']

                folderCorrect = False;
                moveTorrents = moveTorrents + 1;
            # Already been moved, all good
            else:
              folderCorrect = True;

        # RUTRACKER
        # ACTION: IF new, put in seeds/rutracker, copy to_process, set ratio limit
        #         ELSE IF ratio 1:1 then remove it
        elif "ru" in currentTorrent['trackers'][0]['announce']:
            # If it's in the download folder...
            if "/mnt/usb1/downloads/complete/torrents" in currentTorrent['downloadDir']:
                torrentSource =  currentTorrent['downloadDir'] + "/" + currentTorrent['name']
                torrentprocessDestination = "/mnt/usb1/to_process/" + currentTorrent['name']
                torrentseedDestination = "/mnt/usb1/seeds/rutracker/" + currentTorrent['name']

                # Set Ratio Limit
                client('torrent-set',ids=currentTorrent['id'],seedRatioMode=1)


                folderCorrect = False;
                moveTorrents = moveTorrents + 1;
                ruSeeding = ruSeeding + 1;
            # Already been moved, check if seeding complete
            else:
                folderCorrect = True;
                #
                # CHECK IF SEEDING DONE, THEN REMOVE TORRENT / DEL FILES
                #
                if currentTorrent['uploadRatio'] > 0.99:
                        removeTorrents = removeTorrents + 1;
                        deletePath = currentTorrent['downloadDir'] + "/" + currentTorrent['name']
                        print '* DELETED - %s' % (currentTorrent['name'])

                        # delete-local-data argument doesn't work here
                        client('torrent-remove',ids=currentTorrent['id'])
                        # use shutil instead
                        if (os.path.isfile(deletePath) == True):
                          os.remove(deletePath)
                        else:
                                shutil.rmtree(deletePath)
                        ruDeleted = ruDeleted + 1
                else:
                        ruSeeding = ruSeeding + 1;

        # WAFFLES
        elif "waffles" in currentTorrent['trackers'][0]['announce']:
            # If it's in the download folder...
            if "/mnt/usb1/downloads/complete/torrents" in currentTorrent['downloadDir']:
                torrentSource =  currentTorrent['downloadDir'] + "/" + currentTorrent['name']
                torrentprocessDestination = "/mnt/usb1/to_process/" + currentTorrent['name']
                torrentseedDestination = "/mnt/usb1/seeds/waffles/" + currentTorrent['name']

                folderCorrect = False;
                moveTorrents = moveTorrents + 1;
            # Already been moved, all good
            else:
              folderCorrect = True;
        #
        # PUBLIC TORRENTS
        # 
        else:
            removeTorrents = removeTorrents + 1;
            folderCorrect = True;
            print '* REMOVED - %s' % (currentTorrent['name'])

            # Remove It
            client('torrent-remove',ids=currentTorrent['id'])


        #
        # IF TORRENTS NEED TO BE MOVED
        #
        if (folderCorrect == False):
            print '* MOVED - %s' % (currentTorrent['name'])

            # COPY TO PROCESS FOLDER
            if (os.path.isfile(torrentSource) == True):
                shutil.copyfile(torrentSource, torrentprocessDestination)
            else:
                shutil.copytree(torrentSource, torrentprocessDestination)
            # MOVE TO SEEDING FOLDER
            client('torrent-set-location',ids=currentTorrent['id'],location=torrentseedDestination,move='true')

    loop = loop + 1;

downTorrents = totalTorrents - doneTorrents;

print " "
print "TORRENT CLEAN UP:"
print "PUBLIC: %s removed." % (removeTorrents)
print "SEEDS: %s moved to seeds." % (moveTorrents)
print "RU: %s deleted, %s seeding." % (ruDeleted,ruSeeding)
print " "
print "DOWNLOADING: %s torrents." % (downTorrents)
print "SEEDING: %s torrents" % (doneTorrents)
