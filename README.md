This programme will help you to download to a single Excel table statistics on international trade from UN Comtrade website.

The programme requires files reporter_codes_dict.txt and partner_codes_dict.txt which store names and codes of countries.
subscription_key.txt is a file which will store the subctription key from UN Comtrade.

You can get the key here:
Sign up on this website https://comtradedeveloper.un.org/signin?returnUrl=/profile. Go to Products, then to Free APIs.
In section "Your subscriptions" in field "Your new product subscription name" write "comtrade - v1" and subscribe. This is free.
After that you can check your subscriptions in your profile. Press "show" near Primary key.

How this works?
Run the programme. In the Subscription key field, enter the subscription key from the Comtrade API website.
After the first request, this key will be saved to the subscription_key file and will be loaded from there.

1) Select the frequency of data: by year or month.
2) Select periods. In the left part you can select periods one by one. In the right part you can add a range of periods at once. You can add as many single years or ranges as you like.
3) Select reporting countries
4) Select partners
5) Select HS codes of goods. Here you can also select either by piece or by range (or both).
6) Select the direction of trade (export/import/ both)
7) Select whether you want to aggregate the data in some way.
8) Enter the name of the output file and select the format (xlsx or csv).
9) For xlsx files there is a function to group all data by product categories (HS chapters).
10) Click "Load data"

When the programme finishes, it will write a message that the data has been uploaded. The output file will be saved to the folder where the programme lies.

In the "Trade value" column in the summary table for exports - FOB value (the value of goods includes only delivery to the ship),
and for imports - CIF value (the value of goods includes freight to the importing country and insurance).
