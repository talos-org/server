#!/usr/bin/env bash
multichainVersion="multichain-2.0-beta-2"
multichainZipped="$multichainVersion.tar.gz"
multichainLink="https://www.multichain.com/download/$multichainZipped"
curl -o $multichainZipped $multichainLink
tar -xvzf $multichainZipped
cd $multichainVersion
mv multichaind multichain-cli multichain-util /usr/local/bin
cd ..
rm -r $multichainVersion
rm $multichainZipped
