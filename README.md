# torrentcleaner.py
An example of using transmission-fluid to control Transmission queue, manage seed ratios, and sort files based on tracker in Python

* transmission-fluid
  * https://github.com/edavis/transmission-fluid

# Transmission Documentation
* https://trac.transmissionbt.com/browser/trunk/extras/rpc-spec.txt
* http://pythonhosted.org/transmissionrpc/reference/transmissionrpc.html

# What it Does
* Apollo torrents
  * Move torrent to seeds/apollo
  * copy to to_process folder for encoding
* Waffles torrents
  * Move torrent to seeds/waffles
  * Copy to to_process folder for encoding
* RU torrents
  * Move torrent to seeds/rutracker
  * Copy to to_process folder for encoding
  * Enable ratio limit (1:1)
  * Remove torrent and delete files if seeding complete
* Public torrents
  * Remove torrent when complete
  * Leave files where they are (downloads/complete/torrents)
  
  Run by cron every 30 minutes.
