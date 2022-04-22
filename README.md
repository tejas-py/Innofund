
# **INNOFUND-API CONTROLLER**
---

## **1. /create_account:**
Creates Account for user by taking information (username, usertype and email) and returning a unique user id.
Contains Smart Contract where details of the users are passed as the arguments of the application. (user_details.py & user_details.teal)

### Contains check for (in API)-
i) username:
Should be, 6< username >12
Should at least contains one capital letter, one small letter and one number
Shouldn't contain spaces

ii) usertype:
should be a (Investor, investor, Creator or creator)

iii) email:
should be an email address i.e. _email@example.com_

## **2. /create_admin_account:**
Creates account for the admin user by taking information(username, usertype, email and password) and returning a unique admin user id.
Contains smart contract where details of the admin are passed as the arguments of the application. (admin_account_contract.py & admin_account_contract.teal)

### Contains check for (in API)-
i) username:
Should be, 6< username >12
Should at least contains one capital letter, one small letter and one number
Shouldn't contain spaces

ii) usertype:
should be a (Admin, admin or ADMIN)

iii) email:
should be an email address i.e. _email@example.com_

## **3. /update_account:**
Updates the account details of the user i.e. username, usertype and email for the same user id.
Contains Smart Contract where details of the users are passed as the arguments of the application. (user_details.py & user_details.teal)

_API requires: the user passphrase, user id, previous username, previous usertype and previous email_

### Contains check for (in API)-
i) username:
Should be, 6< username >12
Should at least contains one capital letter, one small letter and one number
Shouldn't contain spaces

ii) usertype:
should be a (Investor, investor, Creator or creator)

iii) email:
should be an email address i.e. _email@example.com_

## **4. /update_admin:**
Updates the account details of the admin i.e. username, usertype, email and password for the same admin id.
Contains smart contract where details of the admin are passed as the arguments of the application. (admin_account_contract.py & admin_account_contract.teal)

_API requires: the admin passphrase, user id, previous username, previous usertype, previous email and previous password_

### Contains check for (in API)-
i) username:
Should be, 6< username >12
Should at least contains one capital letter, one small letter and one number
Shouldn't contain spaces

ii) usertype:
should be a (Admin, admin or ADMIN)

iii) email:
should be an email address i.e. _email@example.com_

## **5. /delete_user:**
Delete the account details of Admin, Creator, and Investor.
Contains Smart Contract where it allows to delete admin, creator and investor's accounts.

_API requires: Passphrase, user_id of the account that has to be deleted_

## **6. /create_campaign:**
Create campaign for the creator, by passing the information of the campaign, will generate the unique campaign id.
Contains Smart Contract where details of the campaigns are passed as the arguments of the application. (campaign_approval.py & campaign_approval.teal)

_API requires: creator passphrase, title, description, category, start time, end time, fund category, fund limit, reward type and country._
checks in the smart contract: end time > start time.

## **7. /update_campaign:**
Update the existing campaign details for the same campaign id.
Contains Smart Contract where details of the campaigns are passed as the arguments of the application. (campaign_approval.py & campaign_approval.teal)

_API requires: creator passphrase, campaign id,previous title, previous description, previous category, previous start time, previous end time, previous fund category, previous fund limit, previous reward type and previous country._

###checks in the smart contract: end time > start time.

## **8. /reject_campaign:**
When admin rejects or block the campaign with a reason, that reason gets stored in transaction by calling the campaign id.
Contains smart contract that allow this transaction to occur.

_API requires: passphrase, campaign_id and reason for rejecting or blocking the campaign

## **9. /delete_campaign:**
Delete the campaign details created by the creator
Contains Smart Contract where it allows to delete the campaign.

_API requires: Passphrase, campaign_id of the campaign that has to be deleted_

## **10. /create_asset:**
mint NFT, only by creator, it's a group transaction of admin application call and create asset.
By calling application, it is checked that only admin is minting NFT, if the usertype is creator or investor, then the transaction is declined.

_API requires: admin id, admin passphrase, usertype, password, asset amount, unit name, asset name and url._

## **11. /transfer_asset:**
Transfer NFT from admin to campaign creator, it's a group transaction of campaign application call, creator opting in the asset, transfer of the NFT from admin to creator, and changing the manager, reserve, freeze, and clawback from admin to creator.
By calling the application, it groups the NFT to that particular campaign id.

_API requires: admin passphrase, asset id, campaign id, campaign creator address, asset amount._

## **12. /creator_investor:**
Transfer NFT from Campaign Creator to Investor, it's a group transaction of investor opting in the asset and transfer of asset from creator to investor.

_API requires: in investor passphrase, creator passphrase, asset id, asset amount._

## **13. /burn_asset:**
Destroys the particular asset by creator, it's a group transaction of campaign application call and destroys asset

_API requires: creator passphrase, asset id and campaign id._

## **14. /participating:**
Investors participate in the running campaign by investing sum amount in the campaign. This API update the total investment done in the campaign by using smart contract.

### Smart contracts check:
i) if end date is over than participation cannot be done.
ii) investment amount should be less than the fund limit of the campaign.
iii) investment amount should not exceed the investment still required by campaign.

_API requires: investor passphrase, campaign id, investment amount_

## **15. /pull_investment:**
Creator of the campaign pulls out the investment that was done by the investors in the particular campaign. It's a group transaction of campaign application call and amount transfer from escrow account to creator account.
campaign application call, smart contract checks only if the campaign has ended, the creator is allowed to pull the investment.

_API requires: creator passphrase, campaign id, amount (that has to be pulled by the creator)_

## **16. /total_nft:**
Get total NFT minted by Admin account.

_API requires: admin account public address_

## **17. /account_info:**
Get the account information of particular account.

_API requires: account public address_
