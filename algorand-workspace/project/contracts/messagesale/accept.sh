#!/usr/bin/env bash

# load variables from config file
APP_ID=1
APP_ACCOUNT="WCS6TVPJRBSARHLN2326LRU5BYVJZUKI2VJ53CAWKYYHDE455ZGKANWMGM"
CHALLENGER_ACCOUNT="RGTMYFPZKMEOJELWPIK5AVZ5KWGQWLFYAAVWIMHG5CK4EZKL4BBK2OOFRE"
WAGER=1500
CHALLENGE_B64="1fK8biazjYeoGhCPrUE5MXRpOMp2fvRn8wnfvoTtM5A=" #Uses pyteal_helpers.hash.py to encode a hash in base64
OPPONENT_ACCOUNT="WVR7PIKKBFTFXDKVJC7PLAAP56FUW3X6Q6S7X4KEOZZ22G355XNU4ZKM34"
OPPONENT_OPTING="y"
CHALLENGER_REVEAL="s-143298479749479749"
MESSAGE="SOMEMESSAGE"

# create accept transaction
goal app call \
    --app-id "$APP_ID" \
    -f "$OPPONENT_ACCOUNT" \
    --app-account "$CHALLENGER_ACCOUNT" \
    --app-arg "str:accept" \
    --app-arg "str:$OPPONENT_OPTING" \
    -o accept-call.tx

# create wager transaction
goal clerk send \
    -a "$WAGER" \
    -t "$APP_ACCOUNT" \
    -f "$OPPONENT_ACCOUNT" \
    -o accept-wager.tx

# group transactions
cat accept-call.tx accept-wager.tx > accept-combined.tx
goal clerk group -i accept-combined.tx -o accept-grouped.tx
goal clerk split -i accept-grouped.tx -o accept-split.tx

# sign individual transactions
goal clerk sign -i accept-split-0.tx -o accept-signed-0.tx
goal clerk sign -i accept-split-1.tx -o accept-signed-1.tx

# re-combine individually signed transactions
cat accept-signed-0.tx accept-signed-1.tx > accept-signed-final.tx

# send transaction
goal clerk rawsend -f accept-signed-final.tx
