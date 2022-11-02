from pyteal import *
from Contracts.teal import to_teal


# Smart contract for the Grant
def grant():

    # Checks that the sender is the app creator
    is_app_creator = Txn.sender() == App.globalGet(Bytes('creator'))

    # on creation (constructor)
    on_creation = Seq(
        [
            Assert(Txn.application_args.length() == Int(9)),
            App.globalPut(Bytes("title"), Txn.application_args[0]),
            App.globalPut(Bytes("duration"), Btoi(Txn.application_args[1])),
            App.globalPut(Bytes("min_grant"), Btoi(Txn.application_args[2])),
            App.globalPut(Bytes("max_grant"), Btoi(Txn.application_args[3])),
            App.globalPut(Bytes("total_grants"), Btoi(Txn.application_args[4])),
            App.globalPut(Bytes("total_budget"), Btoi(Txn.application_args[5])),
            App.globalPut(Bytes("grant_end_date"), Btoi(Txn.application_args[6])),
            App.globalPut(Bytes("ESG"), Btoi(Txn.application_args[7])),
            App.globalPut(Bytes('given_grant'), Int(0)),
            App.globalPut(Bytes('status'), Bytes('pending')),
            App.globalPut(Bytes('creator'), Txn.application_args[8]),
            Approve()
        ]
    )

    # when the grant applicant application gets approves, the status for the application changes to approve
    approve_applicant_application_status = Seq(
        Assert(App.globalGet(Bytes('status')) == Bytes('approved')),
        Assert(Btoi(Txn.application_args[4]) < App.globalGet(Bytes('grant_end_date'))),
        InnerTxnBuilder.Begin(),
        # Transaction 1: Applicant's application call to change the status of the applicant's application smart contract
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.ApplicationCall,
            TxnField.application_id: Txn.applications[1],
            TxnField.application_args: [Txn.application_args[1]],
            TxnField.fee: Int(0)
        }),
        InnerTxnBuilder.Next(),
        # Transaction 2: Transfer the grant money to the applicant smart contract
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.Payment,
            # account of the applicant's smart contract
            TxnField.receiver: Txn.accounts[1],
            # Total Ask Amount to be given to the grant applicant smart contract - 10% advance
            TxnField.amount: Btoi(Txn.application_args[2]),
            TxnField.fee: Int(0)
        }),
        InnerTxnBuilder.Next(),
        # Transaction 3: Give advance 10% to the grant applicant to start the milestone
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.Payment,
            # account of the applicant personal wallet
            TxnField.receiver: Txn.accounts[2],
            # 10% advance to be given to the applicant personal wallet
            TxnField.amount: Btoi(Txn.application_args[3]),
            TxnField.fee: Int(0)
        }),
        # Submit the transaction
        InnerTxnBuilder.Submit(),
        # approve the transaction and update the given grant
        App.globalPut(Bytes('given_grant'),
                      App.globalGet(Bytes('given_grant')) + Btoi(Txn.application_args[2]) + Btoi(Txn.application_args[3])),
        Approve()
    )

    # rejecting the grant applicant application and changing tha application status to reject
    reject_applicant_application_status = Seq(
        Assert(App.globalGet(Bytes('status')) == Bytes('approved')),
        InnerTxnBuilder.Begin(),
        # Transaction: Applicant's application call to change the status of the application
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.ApplicationCall,
            TxnField.application_id: Txn.applications[1],
            TxnField.application_args: [Txn.application_args[1]],
            TxnField.fee: Int(0)
        }),
        # Submit the transaction
        InnerTxnBuilder.Submit(),
        Approve()
    )

    # checking all the forms of the application that is applied by the grant applicant
    check_applicant_application = Seq(
        Assert(App.globalGet(Bytes('status')) == Bytes('approved')),
        # app args 1 == current time
        # app args 2 == asl amount
        Assert(Btoi(Txn.application_args[1]) < App.globalGet(Bytes('grant_end_date'))),
        Assert(Btoi(Txn.application_args[2]) < App.globalGet(Bytes('grant_end_date'))),
        Assert(Btoi(Txn.application_args[3]) < App.globalGet(Bytes('grant_end_date'))),
        # check the amount that is asked
        Assert(App.globalGet(Bytes('total_budget')) > App.globalGet(Bytes('given_grant'))),
        Assert(Btoi(Txn.application_args[2]) <= App.globalGet(Bytes('total_budget'))),
        Assert(Btoi(Txn.application_args[2]) >= App.globalGet(Bytes('min_grant'))),
        Assert(Btoi(Txn.application_args[2]) <= App.globalGet(Bytes('max_grant'))),
        Approve()
    )

    # edit the grant details while the status is pending
    edit_grant_details = Seq(
        Assert(App.globalGet(Bytes('status')) == Bytes('pending')),
        App.globalPut(Bytes("title"), Txn.application_args[1]),
        App.globalPut(Bytes("duration"), Btoi(Txn.application_args[2])),
        App.globalPut(Bytes("min_grant"), Btoi(Txn.application_args[3])),
        App.globalPut(Bytes("max_grant"), Btoi(Txn.application_args[4])),
        App.globalPut(Bytes("total_grants"), Btoi(Txn.application_args[5])),
        App.globalPut(Bytes("total_budget"), Btoi(Txn.application_args[6])),
        App.globalPut(Bytes("grant_end_date"), Btoi(Txn.application_args[7])),
        Approve()
    )

    status_change_by_admin = If(
        Btoi(Txn.application_args[1]) == Int(1),
        Seq(
            Assert(App.globalGet(Bytes('status')) == Bytes('pending')),
            App.globalPut(Bytes('status'), Bytes('approved')),
            Approve()
        ),
        Seq(
            Assert(App.globalGet(Bytes('status')) == Bytes('pending')),
            App.globalPut(Bytes('status'), Bytes('rejected')),
            Approve()
        )
    )

    call_transactions = Cond(
        # Condition 1
        [And(
            Global.group_size() == Int(3),
            Txn.application_args[0] == Bytes("Apply for grant")
        ), check_applicant_application],
        # Condition 2
        [And(
            is_app_creator,
            Txn.application_args[0] == Bytes("Approve grant application")
        ), approve_applicant_application_status],
        # Condition 3
        [Txn.application_args[0] == Bytes("Reject grant application"), reject_applicant_application_status],
        # Condition 4
        [And(
            is_app_creator,
            Txn.application_args[0] == Bytes('Edit Grant')
        ), edit_grant_details],
        # Condition 5
        [Txn.application_args[0] == Bytes('Approve/Reject Grant by Admin'), status_change_by_admin]
    )

    # Smart contract Balance
    my_balance = AccountParam.balance(Global.current_application_address())

    # check the status of the Grant
    delete_cond_check = Seq(
        my_balance,
        Assert(Or(
            App.globalGet(Bytes('status')) == Bytes('rejected'),
            App.globalGet(Bytes('status')) == Bytes('pending'),
            my_balance.value() == Int(0),
        )),
        Approve()
    )

    # Delete Grant and Transfer the Grant Amount
    delete_cond = Seq(
        Assert(is_app_creator),
        Assert(Global.group_size() == Int(2)),
        # Pay the remaining amount inside the Grant to Grant Creator/Manager
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.Payment,
            TxnField.close_remainder_to: Global.creator_address(),
            TxnField.fee: Int(0)
        }),
        # Submit the transaction
        InnerTxnBuilder.Submit(),
        delete_cond_check
    )

    program = Cond(
        [Txn.application_id() == Int(0), on_creation],
        [Txn.on_completion() == OnComplete.NoOp, call_transactions],
        [Txn.on_completion() == OnComplete.DeleteApplication, delete_cond]
    )

    return program


# Smart Contract for the Grant Creator: Manager
def manager():

    # define the grant application id
    grant_application_id = AppParam.address(InnerTxn.created_application_id())

    # approval and clear program for child application
    app_prog_teal = to_teal(grant())
    clear_prog_teal = to_teal(clearstate_contract())

    # Checks that the sender is the app creator
    is_app_creator = Txn.sender() == Global.creator_address()

    # check the balance of the smart contract
    my_balance = AccountParam.balance(Global.current_application_address())

    # on creation (constructor)
    on_creation = Seq(
        [
            Assert(Txn.application_args.length() == Int(2)),
            App.globalPut(Bytes("organisation_name"), Txn.application_args[0]),
            App.globalPut(Bytes("usertype"), Txn.application_args[1]),
            Approve()
        ]
    )

    # do the payment to the grant
    payment_to_grant = Seq(
        grant_application_id,
        InnerTxnBuilder.Begin(),
        # Transaction: Payment to the grant smart contract
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.Payment,
            TxnField.receiver: grant_application_id.value(),
            TxnField.amount: Btoi(Txn.application_args[6]), # total grant
            TxnField.fee: Int(0),
        }),
        # Submit the transaction
        InnerTxnBuilder.Submit(),
        Approve()
    )

    # creating grant smart contract
    create_grant_inner_txn = Seq(
        my_balance,
        Assert(my_balance.value()),
        Seq(
            InnerTxnBuilder.Begin(),
            # Transaction: Create child smart contract
            InnerTxnBuilder.SetFields({
                TxnField.type_enum: TxnType.ApplicationCall,
                TxnField.global_num_byte_slices: Int(3),
                TxnField.global_num_uints: Int(8),
                TxnField.approval_program: Bytes(app_prog_teal),
                TxnField.clear_state_program: Bytes(clear_prog_teal),
                TxnField.application_args: [
                    Txn.application_args[1], Txn.application_args[2], Txn.application_args[3], Txn.application_args[4],
                    Txn.application_args[5], Txn.application_args[6], Txn.application_args[7], Txn.application_args[8],
                    Txn.sender()
                ],
                TxnField.on_completion: OnComplete.NoOp,
                TxnField.fee: Int(0)
            }),
            # Submit the transaction
            InnerTxnBuilder.Submit(),
        ),
        payment_to_grant
    )

    # create grant cond
    create_grant_cond = Seq(
        Assert(Global.group_size() == Int(2)),
        Assert(Gtxn[0].type_enum() == TxnType.Payment),
        Assert(Gtxn[1].type_enum() == TxnType.ApplicationCall),
        create_grant_inner_txn
    )

    # Delete Grant Inner Txn
    delete_grant_inner_txn = Seq(
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.ApplicationCall,
            TxnField.application_id: Txn.applications[1],
            TxnField.on_completion: OnComplete.DeleteApplication,
            TxnField.fee: Int(0)
        }),
        InnerTxnBuilder.Next(),
        # Transaction: Payment to grant creator
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.Payment,
            TxnField.amount: Int(578000),
            TxnField.receiver: Global.creator_address(),
            TxnField.fee: Int(0)
        }),
        # Submit the transaction
        InnerTxnBuilder.Submit(),
        Approve()
    )

    # application call transactions
    call_transactions = Cond(
        [Txn.application_args[0] == Bytes("Create Grant"), create_grant_cond],
        [Txn.application_args[0] == Bytes("Delete Grant"), delete_grant_inner_txn],
    )

    program = Cond(
        [Txn.application_id() == Int(0), on_creation],
        [Txn.on_completion() == OnComplete.NoOp, call_transactions],
        [Txn.on_completion() == OnComplete.DeleteApplication, Cond([is_app_creator, Approve()])]
    )

    return program


# Smart Contract for the grant creator
def admin():

    # Grant Application id
    grant_application_id = AppParam.address(InnerTxn.created_application_id())

    # approval and clear program for child application and grant
    app_prog_teal = to_teal(manager())
    clear_prog_teal = to_teal(clearstate_contract())
    app_prog_teal_grant = to_teal(grant())

    # check the balance of the smart contract
    my_balance = AccountParam.balance(Global.current_application_address())

    # Checks that the sender is the app creator
    is_app_creator = Txn.sender() == Global.creator_address()

    on_creation = Seq(
        [
            Assert(Txn.application_args.length() == Int(3)),
            App.globalPut(Bytes("organisation_name"), Txn.application_args[0]),
            App.globalPut(Bytes("organisation_role"), Txn.application_args[1]),
            App.globalPut(Bytes("usertype"), Txn.application_args[2]),
            Approve()
        ]
    )

    # create smart contract for the Grant Creator: Manager
    create_manager_inner_txn = Seq(
        InnerTxnBuilder.Begin(),
        # Transaction: Create child smart contract
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.ApplicationCall,
            TxnField.global_num_byte_slices: Int(2),
            TxnField.global_num_uints: Int(0),
            TxnField.approval_program: Bytes(app_prog_teal),
            TxnField.clear_state_program: Bytes(clear_prog_teal),
            TxnField.application_args: [App.globalGet(Bytes("organisation_name")), Txn.application_args[1]],
            TxnField.on_completion: OnComplete.NoOp,
            TxnField.fee: Int(0)
        }),
        # Submit the transaction
        InnerTxnBuilder.Submit(),
        Approve()
    )

    # Create Manager Conditions
    create_manager_cond = Seq(
        Assert(is_app_creator),
        Assert(Global.group_size() == Int(2)),
        Assert(Gtxn[0].type_enum() == TxnType.Payment),
        Assert(Gtxn[1].type_enum() == TxnType.ApplicationCall),
        create_manager_inner_txn
    )

    # do the payment to the grant
    payment_to_grant = Seq(
        grant_application_id,
        InnerTxnBuilder.Begin(),
        # Transaction: Payment to the grant smart contract
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.Payment,
            TxnField.receiver: grant_application_id.value(),
            TxnField.amount: Btoi(Txn.application_args[6]), # total grant
            TxnField.fee: Int(0),
        }),
        # Submit the transaction
        InnerTxnBuilder.Submit(),
        Approve()
    )

    # creating grant smart contract
    create_grant_inner_txn = Seq(
        my_balance,
        Assert(my_balance.value()),
        Seq(
            InnerTxnBuilder.Begin(),
            # Transaction: Create child smart contract
            InnerTxnBuilder.SetFields({
                TxnField.type_enum: TxnType.ApplicationCall,
                TxnField.global_num_byte_slices: Int(3),
                TxnField.global_num_uints: Int(8),
                TxnField.approval_program: Bytes(app_prog_teal_grant),
                TxnField.clear_state_program: Bytes(clear_prog_teal),
                TxnField.application_args: [
                    Txn.application_args[1], Txn.application_args[2], Txn.application_args[3], Txn.application_args[4],
                    Txn.application_args[5], Txn.application_args[6], Txn.application_args[7], Txn.application_args[8],
                    Global.creator_address()
                ],
                TxnField.on_completion: OnComplete.NoOp,
                TxnField.fee: Int(0)
            }),
            # Submit the transaction
            InnerTxnBuilder.Submit()
        ),
        payment_to_grant
    )

    # create grant cond
    create_grant_cond = Seq(
        Assert(Global.group_size() == Int(2)),
        Assert(Gtxn[0].type_enum() == TxnType.Payment),
        Assert(Gtxn[1].type_enum() == TxnType.ApplicationCall),
        create_grant_inner_txn
    )

    # Delete Grant Inner Txn
    delete_grant_inner_txn = Seq(
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.ApplicationCall,
            TxnField.application_id: Txn.applications[1],
            TxnField.on_completion: OnComplete.DeleteApplication,
            TxnField.fee: Int(0)
        }),
        InnerTxnBuilder.Next(),
        # Transaction: Payment to grant creator
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.Payment,
            TxnField.amount: Int(578000),
            TxnField.receiver: Global.creator_address(),
            TxnField.fee: Int(0)
        }),
        # Submit the transaction
        InnerTxnBuilder.Submit(),
        Approve()
    )

    # Application Call transactions
    call_transactions = Cond(
        [Txn.application_args[0] == Bytes("Create Manager"), create_manager_cond],
        [Txn.application_args[0] == Bytes("Create Grant"), create_grant_cond],
        [Txn.application_args[0] == Bytes("Delete Grant"), delete_grant_inner_txn]
    )

    program = Cond(
        [Txn.application_id() == Int(0), on_creation],
        [Txn.on_completion() == OnComplete.NoOp, call_transactions],
        [Txn.on_completion() == OnComplete.DeleteApplication, Cond([is_app_creator, Approve()])]
    )

    return program


# clear program for the grant creator, manager and the grant
def clearstate_contract():
    return Approve()


if __name__ == "__main__":
    with open("teal_test.teal", "w") as f:
        compiled = compileTeal(admin(), mode=Mode.Application, version=6)
        f.write(compiled)
