INNOFUND - written in Python and Pyteal


API Controller

1. /create_account:
Creates Account for user by taking information (username, usertype and email) and returning an unique user id.
Contains Smart Contract where details of the users are passed as the arguments of the application. (user_details.py & user_details.teal)

Contains check for (in API)-
i) username:
Should be, 6< username >12
Should atleast contains one capital letter, one small letter and one number
Shouldnot contain spaces

ii) usertype:
should be a (Investor, investor, Creator or creator)

iii) email:
should be an email address i.e. ___@___.___



2. /create_admin_account:
Creates account for the admin user by taking information(username, usertype, email and password) and returning an unique admin user id.
Contains smart contract where details of the admin are passed as the arguments of the application. (admin_account_contract.py & admin_account_contract.teal)

Contains check for (in API)-
i) username:
Should be, 6< username >12
Should atleast contains one capital letter, one small letter and one number
Shouldnot contain spaces

ii) usertype:
should be a (Admin, admin or ADMIN)

iii) email:
should be an email address i.e. ___@___.___



3. /update_account:
Updates the account details of the user i.e username, usertype and email for the same user id.
Contains Smart Contract where details of the users are passed as the arguments of the application. (user_details.py & user_details.teal)
API requires: the user passphrase, user id, previous username, previous usertype and previous email

Contains check for (in API)-
i) username:
Should be, 6< username >12
Should atleast contains one capital letter, one small letter and one number
Shouldnot contain spaces

ii) usertype:
should be a (Investor, investor, Creator or creator)

iii) email:
should be an email address i.e. ___@___.___



4. /update_admin:
Updates the account details of the admin i.e username, usertype, email and password for the same admin id.
Contains smart contract where details of the admin are passed as the arguments of the application. (admin_account_contract.py & admin_account_contract.teal)
API requires: the admin passphrase, user id, previous username, previous usertype, previous email and previous password

Contains check for (in API)-
i) username:
Should be, 6< username >12
Should atleast contains one capital letter, one small letter and one number
Shouldnot contain spaces

ii) usertype:
should be a (Admin, admin or ADMIN)

iii) email:
should be an email address i.e. ___@___.___



5. /create_campaign:
Create campaign for the creator, by passing the information of the campaign, will generate the unique campaign id.
Contains Smart Contract where details of the campaings are passed as the arguments of the application. (campaign_approval.py & campaign_approval.teal)
API requires: creator passphrase, title, description, category, start time, end time, fund category, fund limit, reward type and country.
checks in the smart contract: end time > start time.



6. /update_campaign:
Update the existing campaign details for the same campaign id.
Contains Smart Contract where details of the campaings are passed as the arguments of the application. (campaign_approval.py & campaign_approval.teal)
API requires: creator passphrase, campaign id,previous title, previous description, previous category, previous start time, previous end time, previous fund category, previous fund limit, previous reward type and previous country.
checks in the smart contract: end time > start time.



7. /create_asset:
mint NFT, only by creator, its a group transaction of admin application call and create asset.
By calling application, it is checked that only admin is minting NFT, if the usertype is creator or investor, then the transaction is declined.
API requires: admin id, admin passphrase, usertype, password, asset amount, unit name, asset name and url



8. /transfer_asset:
Transfer NFT from admin to campaign creator, its a group transaction of campaign application call, creator opting in the asset, transfer of the NFT from admin to creator, and changing the manager, reserve, freeze, and clawback from admin to creator.
By calling the application, it groups the NFT to that perticular campaign id.
API requires: admin passphrase, asset id, campaign id, campaign creator address, asset amount



9. /creator_investor:
Transfer NFT from Campaign Creator to Investor, its a group transaction of investor opting in the asset and transfer of asset from creator to investor.
API requires: in investor passphrase, creator passphrase, asset id, asset amount



10. /burn_asset:
Destorys the particular asset by creator, its a group transaction of campaign application call and destorys asset
API requires: creator passphrase, asset id and campaign id



11. /participating:
Investors participate in the running campaign by investing sum amount in the campaign. This API update the total investment done in the campaign by using smart contract.
Smart contracts check:
i) if end date is over than participation cannot be done.
ii) investment amount should be less then the fund limit of the campaign.
iii) investment amount should not exceed the investment still required by campaign.

API requires: investor passphrase, campaign id, investment amount



12. /pull_investment:
Creator of the campaign pulls out the investment that was done by the investors in the particular campaign. Its a group transaction of campaign application call and amount transfer from escrow account to creator account.
campaign application call, smart contract checks only if the campaign has ended, the creator is allowed to pull the investment.

API requires: creator passphrase, campaign id, amount (that has to be pulled by the creator)