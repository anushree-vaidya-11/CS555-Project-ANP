from pyteal import *
from pyteal.ast.bytes import Bytes
from pyteal_helpers import program

def approval():
    # locals
    local_opponent = Bytes("opponent")  # byteslice - client/dealer
    local_wager = Bytes("wager")  # uint64 - price
    local_message = Bytes("message")  # byteslice - Hash   
    local_reveal = Bytes("reveal")  # byteslice

    op_challenge = Bytes("challenge") #First method that get's called to start the sale (and put the message?)
    op_accept = Bytes("accept") #Client will call to accept the challange (and pay?)
    op_reveal = Bytes("reveal") #Validate the payment and reveal the message to client 

    @Subroutine(TealType.none)
    def reset(account: Expr):
        return Seq(
            App.localPut(account, local_opponent, Bytes("")),
            App.localPut(account, local_wager, Int(0)),
            App.localPut(account, local_message, Bytes("")),
            App.localPut(account, local_reveal, Bytes("")),
        )

    @Subroutine(TealType.uint64)
    def is_empty(account: Expr):
        return Return(
            And(
                App.localGet(account, local_opponent) == Bytes(""),
                App.localGet(account, local_wager) == Int(0),
                App.localGet(account, local_message) == Bytes(""),
                App.localGet(account, local_reveal) == Bytes(""),
            )
        )

    # @Subroutine(TealType.uint64) #Checking if the first letter is r,p or s for rock, paper or scissors.In our case, we'd need to check if we have a particular encryption
    # def is_valid_play(p: Expr):
    #     first_letter = ScratchVar(TealType.bytes)
    #     return Seq(
    #         first_letter.store(Substring(p, Int(0), Int(1))),
    #         Return(
    #             Or(
    #                 first_letter.load() == Bytes("r"),
    #                 first_letter.load() == Bytes("p"),
    #                 first_letter.load() == Bytes("s"),
    #             )
    #         ),
    #     )

    @Subroutine(TealType.none) #This has transaction grouping 'cause it needs a challenge and a wager
    def create_challenge():
        return Seq(
            # basic sanity checks
            program.check_self( #Must have condition according to Docs
                group_size=Int(2), #There are two items in the group
                group_index=Int(0), #The transaction that is calling the create challenge subroutine is the first transaction(us)
            ),
            program.check_rekey_zero(2),
            Assert(
                And(
                    # second transaction is wager payment (first is us)
                    Gtxn[1].type_enum() == TxnType.Payment, #check if transaction type is payment
                    Gtxn[1].receiver() == Global.current_application_address(), #The money should go to the address(account) of the current application 
                    Gtxn[1].close_remainder_to() == Global.zero_address(), #Must haves according to the docs https://developer.algorand.org/docs/get-details/dapps/avm/teal/guidelines/
                    # second account has opted-in
                    App.optedIn(Int(1), Int(0)), #check that the opponent(client) has opted in to the current app(challenge)
                    is_empty(Int(0)), # Check to make sure that both parties are not currently involved in any other game/challenge
                    is_empty(Int(1)),
                    # commitment
                    Txn.application_args.length() == Int(1), #Accept a hashed commitment(the message) from challenger and store it in the local commitment variable
                )
            ),
            App.localPut(Txn.sender(), local_opponent, Txn.accounts[1]), #Get opponent(client) from 2nd arg of Transaction.accounts. Format - (account,key,value)
            App.localPut(Txn.sender(), local_wager, Gtxn[1].amount()), #Get wager amount from 2nd arg to GTransaction.amount
            # App.localPut( #Get commitment value from 2nd argument to Transaction.application args
            #     Txn.sender(), 
            #     local_message,
            #     Txn.application_args[1],
            # ),
            Approve(),
        )

    @Subroutine(TealType.none)
    def accept_challenge():
        return Seq(
            # basic sanity checks
            program.check_self(
                group_size=Int(2),
                group_index=Int(0),
            ),
            program.check_rekey_zero(2),
            Assert(
                And(
                    # second (opponent) account has opted-in
                    App.optedIn(Int(1), Int(0)),
                    # second account has challenged this account
                    App.localGet(Int(1), local_opponent) == Txn.sender(),
                    # second transaction is wager match
                    Gtxn[1].type_enum() == TxnType.Payment, # Check if it's a wager payment transaction
                    Gtxn[1].receiver() == Global.current_application_address(), # The receiver is our application's wallet address
                    Gtxn[1].close_remainder_to() == Global.zero_address(),
                    Gtxn[1].amount() == App.localGet(Int(1), local_wager), # Amount is the one that's asked 
                    # no commitment on accept, just instant reveal
                    Txn.application_args.length() == Int(1),
                    # is_valid_play(Txn.application_args[1]),
                )
            ),
            App.localPut(Int(0), local_opponent, Txn.accounts[1]),
            App.localPut(Int(0), local_wager, Gtxn[1].amount()),
            send_reward(App.localGet(Int(0), local_wager)), #Payment
            # App.localPut(Int(0), local_reveal, Txn.application_args[1]),
            Approve(),
        )

    # @Subroutine(TealType.uint64) #Map 'rock' to 0, paper to 1 and scissor to 2
    # def play_value(p: Expr):
    #     first_letter = ScratchVar()
    #     return Seq(
    #         first_letter.store(Substring(p, Int(0), Int(1))),
    #         Return(
    #             Cond(
    #                 [first_letter.load() == Bytes("r"), Int(0)],
    #                 [first_letter.load() == Bytes("p"), Int(1)],
    #                 [first_letter.load() == Bytes("s"), Int(2)],
    #             )
    #         ),
    #     )

    # @Subroutine(TealType.uint64)
    # def winner_account_index(play: Expr, opponent_play: Expr):
    #     return Return(
    #         Cond(
    #             [play == opponent_play, Int(2)],  # tie
    #             [(play + Int(1)) % Int(3) == opponent_play, Int(1)],  # opponent wins
    #             [
    #                 (opponent_play + Int(1)) % Int(3) == play,
    #                 Int(0),
    #             ],  # current account win
    #         )
    #     )

    @Subroutine(TealType.none)
    def send_reward(amount: Expr):
        return Seq(
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields(
                {
                    TxnField.type_enum: TxnType.Payment,
                    TxnField.receiver: Txn.accounts[Int(0)],
                    TxnField.amount: amount,
                }
            ),
            InnerTxnBuilder.Submit(),
        )

    @Subroutine(TealType.none)
    def reveal():   #Reveal the winner 
        # winner = ScratchVar() 
        # App.localPut(Int(0), local_message, Txn.application_args[1]),
        message = ScratchVar()
        wager = ScratchVar()
        return Seq(
            # basic sanity checks
            program.check_self(
                group_size=Int(1), #Since we've already completed the payment by now, we only have 1 transaction in the group
                group_index=Int(0), #Make sure that we are that transaction
            ),
            program.check_rekey_zero(1),
            Assert(
                And(
                    # verify game data matches
                    App.localGet(Int(0), local_opponent) == Txn.accounts[1], # Make sure that the opponent is the right opponent (account1)
                    App.localGet(Int(1), local_opponent) == Txn.sender(), #Check that the opponent of that opponent is us
                    App.localGet(Int(0), local_wager) #Make sure that the wager value of both of the accounts are set
                    == App.localGet(Int(1), local_wager), #Make sure that the receiver's local wager is same as the sender's local wager
                    # this account has commitment
                    # App.localGet(Int(0), local_message) != Bytes(""), #The commitment by the challenger is not empty
                    # opponent account has a reveal
                    App.localGet(Int(1), local_reveal) != Bytes(""), #Make sure that the opponent has called the accept function and accepted the challenge
                    # require reveal argument
                    Txn.application_args.length() == Int(2), #accept an additional argument that is the 'reveral'. Make sure that it is actually sent
                    # validate reveal
                    # Sha256(Txn.application_args[1]) #Hash that reveal argument
                    # == App.localGet(Int(0), local_message), #Make sure that the hash matches the challeneger's commitment(that sender hasn't changed his play)
                )
            ),
            App.localPut( #Get commitment value from 2nd argument to Transaction.application args
                Txn.sender(), 
                local_message,
                Txn.application_args[1],
            ),
            wager.store(App.localGet(Int(0), local_wager)),
            message.store(App.localGet(Int(0),local_message)),
            # winner.store(
            #     winner_account_index(
            #         play_value(Txn.application_args[1]),
            #         play_value(App.localGet(Int(1), local_reveal)),
            #     )
            # ),
            # If(winner.load() == Int(2))
            # .Then(
            #     Seq(
            #         # tie: refund wager to each party
            #         send_reward(Int(0), wager.load()),
            #         send_reward(Int(1), wager.load()),
            #     )
            # )
            # .Else(
                # send double wager to winner
            
            
            # ),
            reset(Int(0)),
            reset(Int(1)),
            Approve(),
        )

    return program.event(
        init=Approve(), #We don't need to do anything here because we're doing everything locally inside sandbox
        opt_in=Seq(
            reset(Int(0)), #Initialize all the local variables to be emtpty at first
            Approve(),
        ),
        no_op=Seq(
            Cond(
                [
                    Txn.application_args[0] == op_challenge, #Check if first argument(what's to be done) is op_challenge and if it is,
                    create_challenge(), #call create challenge subroutine
                ],
                [
                    Txn.application_args[0] == op_accept,#Check if first argument is op_accept and if it is,
                    accept_challenge(),#call accept challenge subroutine
                ],
                [
                    Txn.application_args[0] == op_reveal,#Check if first argument is op_reveal and if it is,
                    reveal(),#call reveal challenge subroutine
                ],
            ),
            Reject(),
        ),
    )


def clear():
    return Approve()
