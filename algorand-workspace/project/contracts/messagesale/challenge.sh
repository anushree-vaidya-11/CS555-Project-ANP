#!/usr/bin/env bash

# load variables from config file
# source "$(dirname ${BASH_SOURCE[0]})/config.sh"
APP_ID=1
APP_ACCOUNT="WCS6TVPJRBSARHLN2326LRU5BYVJZUKI2VJ53CAWKYYHDE455ZGKANWMGM"
CHALLENGER_ACCOUNT="RGTMYFPZKMEOJELWPIK5AVZ5KWGQWLFYAAVWIMHG5CK4EZKL4BBK2OOFRE"
WAGER=1500
CHALLENGE_B64="1fK8biazjYeoGhCPrUE5MXRpOMp2fvRn8wnfvoTtM5A=" #Uses pyteal_helpers.hash.py to encode a hash in base64
OPPONENT_ACCOUNT="WVR7PIKKBFTFXDKVJC7PLAAP56FUW3X6Q6S7X4KEOZZ22G355XNU4ZKM34"
OPPONENT_OPTING="y"
CHALLENGER_REVEAL="s-143298479749479749"
MESSAGE="SOMEMESSAGE"

# create challenge transaction 
#call whatever the app id is  
#the account from which the challenge is generating
#Specify the account that is added to the list of extra accounts that the contract is allowed to access within this transaction
#datatype:what function we are calling
#Base 64 encoding of the challenge
#Since the required group size is 2, the transaction otherwise is invalid. So instead of sending it right away, output it to a file
goal app call \
    --app-id "$APP_ID" \ 
    -f "$CHALLENGER_ACCOUNT" \
    --app-account "$OPPONENT_ACCOUNT" \ 
    --app-arg "str:challenge" \ 
    # --app-arg "str:$MESSAGE" \ 
    -o challenge-call.tx 
    
# create wager transaction
goal clerk send \
    -a "$WAGER" \
    -t "$APP_ACCOUNT" \
    -f "$CHALLENGER_ACCOUNT" \
    -o challenge-wager.tx

# group transactions
cat challenge-call.tx challenge-wager.tx > challenge-combined.tx #Make challenge transaction as 1st and payment as 2nd, combine and output to a file
goal clerk group -i challenge-combined.tx -o challenge-grouped.tx #Group them together with a group id
goal clerk split -i challenge-grouped.tx -o challenge-split.tx #Split the group transaction from 1 file into multiple files(2)

# sign individual transactions
goal clerk sign -i challenge-split-0.tx -o challenge-signed-0.tx #sign each of those transactions individually
goal clerk sign -i challenge-split-1.tx -o challenge-signed-1.tx

# re-combine individually signed transactions
cat challenge-signed-0.tx challenge-signed-1.tx > challenge-signed-final.tx #Concatenate them back together

# send transaction
goal clerk rawsend -f challenge-signed-final.tx
