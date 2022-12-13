# shioaji-options
使用永豐API實現選擇權實時自動下單

## Enviorment requirement:
* Python 3.6-3.8
* Shioaji
* virtualenv
  * https://hackmd.io/ouzfodBiR7asRZspTXdq2Q

## operation explaination
- Please read 自動下單及平倉整合說明.txt before started.

## CA setup:
- 申請憑證前須簽屬相關文件，參照以下網址
  - https://www.sinotrade.com.tw/ec/20191125/Main/index.aspx#pag1
- 憑證下載教學
  - https://www.sinotrade.com.tw/ec/eleader1/CAAPQA.pdf
   
## Enviorment setup:

First install python 3.6-3.8 on your computer.
Then run ```pip install shioaji``` on the cmd.

For windows, conda is recommended. Create a new enviorment with python with python3.6-3.8, and run ```pip install shioaji```.

For windows, place your CA signatures under "C:\sinopac", edit account_info.json to specify the file name.

## Usage:

Simply run shioaji_coverer.py and place orders.
DO NOT run if today is WEDNESDAY.
