from pyteal import *
from Contracts.teal import to_teal


# approval program for the grant application, has to be created between two accounts. ie, grant creator and grant applicant
def grant_application():

    # Checks the account address
    is_app_creator = Txn.sender() == Global.creator_address()

    on_creation = Seq(
        [
            Assert(Txn.application_args.length() == Int(4)),
            App.globalPut(Bytes("grant_app_id"), Btoi(Txn.application_args[0])),
            App.globalPut(Bytes("milestone_1"), Txn.application_args[1]),
            App.globalPut(Bytes("milestone_2"), Txn.application_args[2]),
            App.globalPut(Bytes("requested_funds"), Btoi(Txn.application_args[3])),
            App.globalPut(Bytes("status"), Bytes('pending')),
            Approve()
        ]
    )

    approve_application = Seq(
        App.globalPut(Bytes('status'), Bytes('approved')),
        Approve()
    )

    reject_application = Seq(
        App.globalPut(Bytes('status'), Bytes('rejected')),
        Approve()
    )

    edit_grant_application = Seq(
        Assert(App.globalGet(Bytes('status')) == Bytes('pending')),
        App.globalPut(Bytes("milestone_1"), Txn.application_args[1]),
        App.globalPut(Bytes("milestone_2"), Txn.application_args[2]),
        App.globalPut(Bytes("requested_funds"), Btoi(Txn.application_args[3])),
        Approve()
    )

    transfer_money_for_milestone1 = Seq(
        InnerTxnBuilder.Begin(),
        # Transaction: Give Milestone 1 (excluding advance) Money and 10% adv of Mile2
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.Payment,
            # account of the applicant personal wallet
            TxnField.receiver: Txn.accounts[1],
            # amount to be given to the applicant for the milestone 1 payment excluding advance
            # 10% advance to be given to the applicant personal wallet for milestone 2
            TxnField.amount: Btoi(Txn.application_args[1]),
            TxnField.fee: Int(0)
        }),
        # Submit the transaction
        InnerTxnBuilder.Submit(),
        Approve()
    )

    transfer_money_for_milestone2 = Seq(
        InnerTxnBuilder.Begin(),
        # Transaction: Give Milestone 2 (excluding advance) Money after the approval of the report
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.Payment,
            # account of the applicant personal wallet
            TxnField.receiver: Txn.accounts[1],
            # amount to be given to the applicant for the milestone 2 payment excluding advance
            TxnField.amount: Btoi(Txn.application_args[2]),
            TxnField.close_remainder_to: Txn.accounts[1],
            TxnField.fee: Int(0)
        }),
        # Submit the transaction
        InnerTxnBuilder.Submit(),
        App.globalPut(Bytes('status'), Bytes('completed')),
        Approve()
    )

    # change the status of the applicant smart contract to reject and give back the grant money to the creator/manager
    transfer_money_back_to_grant_creator = Seq(
        InnerTxnBuilder.Begin(),
        # Transaction: Milestone report denied, give the remaining balance to the grant creator
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.Payment,
            # account of the grant creator/manager
            TxnField.receiver: Txn.accounts[1],
            # give all the balance of the smart contract to the grant creator
            TxnField.close_remainder_to: Txn.accounts[1],
            TxnField.amount: Btoi(Txn.application_args[1]),
            TxnField.fee: Int(0)
        }),
        # Submit the transaction
        InnerTxnBuilder.Submit(),
        reject_application
    )

    call_transactions = Cond(
        # Condition 1
        [And(
            Global.group_size() == Int(3),
            Txn.application_args[0] == Bytes("Change status to approve")
        ), approve_application],
        # Condition 2
        [Txn.application_args[0] == Bytes("Change status to rejected"), reject_application],
        # Condition 3
        [And(
            is_app_creator,
            Txn.application_args[0] == Bytes('Edit Grant Application')
        ), edit_grant_application],
        # Condition 4: Transfer money for milestone 1 excluding the advance money + Advance money for the milestone 2
        [And(
            Txn.application_args[0] == Bytes('Approve Milestone 1')
        ), transfer_money_for_milestone1],
        # Condition 5: Transfer money for milestone 2 excluding the advance money
        [And(
            Txn.application_args[0] == Bytes('Approve Milestone 2')
        ), transfer_money_for_milestone2],
        # Condition 6: Reject Milestone 1 Report, change the status of applicant smart contract to rejected and give the remaining amount to the grant creator
        [And(
            Txn.application_args[0] == Bytes('Reject Milestone')
        ), transfer_money_back_to_grant_creator]
    )

    delete_cond = Cond(
        [And(
            is_app_creator,
            App.globalGet(Bytes('status')) == Bytes('rejected'),
            App.globalGet(Bytes('status')) == Bytes('pending'),
            App.globalGet(Bytes('status')) == Bytes('completed')
        ), Approve()]
    )
    program = Cond(
        [Txn.application_id() == Int(0), on_creation],
        [Txn.on_completion() == OnComplete.NoOp, call_transactions],
        [Txn.on_completion() == OnComplete.DeleteApplication, delete_cond]
    )

    return program


# approval program for grant applicant
def grant_applicant():

    # grant application smart contract
    approval_program_teal = Bytes(to_teal(grant_application()))
    clear_prog_teal = Bytes(to_teal(clearstate_contract()))

    # Checks that the sender is the app creator
    is_app_creator = Txn.sender() == Global.creator_address()

    on_creation = Seq(
        [
            Assert(Txn.application_args.length() == Int(1)),
            App.globalPut(Bytes("usertype"), Txn.application_args[0]),
            Approve()
        ]
    )

    # inner transaction to create a smart contract for grant application
    create_grant_app_inner_txn = Seq(
        InnerTxnBuilder.Begin(),
        # Transaction: Create child smart contract
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.ApplicationCall,
            TxnField.global_num_byte_slices: Int(3),
            TxnField.global_num_uints: Int(2),
            TxnField.approval_program: approval_program_teal,
            TxnField.clear_state_program: clear_prog_teal,
            TxnField.application_args: [
                Txn.application_args[1], Txn.application_args[2], Txn.application_args[3], Txn.application_args[4]
            ],
            TxnField.on_completion: OnComplete.NoOp,
            TxnField.fee: Int(0)
        }),
        # Submit the transaction
        InnerTxnBuilder.Submit(),
        Approve()
    )

    # conditions for creating grant application
    create_grant_app_cond = Seq(
        Assert(is_app_creator),
        Assert(Gtxn[0].type_enum() == TxnType.Payment),
        Assert(Gtxn[1].type_enum() == TxnType.ApplicationCall),
        Assert(Gtxn[2].type_enum() == TxnType.ApplicationCall),
        create_grant_app_inner_txn
    )

    # Application Call transactions
    call_transactions = Cond(
        [And(
            Global.group_size() == Int(3),
            Txn.application_args[0] == Bytes("Create Grant Application")
        ), create_grant_app_cond]
    )

    program = Cond(
        [Txn.application_id() == Int(0), on_creation],
        [Txn.on_completion() == OnComplete.NoOp, call_transactions],
        [Txn.on_completion() == OnComplete.DeleteApplication, Cond([is_app_creator, Approve()])]
    )

    return program


# clear program for the grant applicant
def clearstate_contract():
    return Approve()
