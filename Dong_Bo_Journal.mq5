//+------------------------------------------------------------------+
//|                                             Dong_Bo_Journal.mq5  |
//|                         Trading Journal - MQL5 Sync Script       |
//|         Dong bo lich su giao dich truc tiep tu MT5 len Web       |
//+------------------------------------------------------------------+
#property copyright "Trading Journal"
#property link      "https://crypto-journal-twhs.onrender.com/"
#property version   "1.00"
#property script_show_inputs

input int InpDaysBack = 90; // So ngay quet lich su (Mac dinh 90 ngay)

//+------------------------------------------------------------------+
//| Script program start function                                    |
//+------------------------------------------------------------------+
void OnStart()
{
   Print("=== BAT DAU DONG BO LENH LEN TRADING JOURNAL ===");
   
   string server = AccountInfoString(ACCOUNT_SERVER);
   long login = AccountInfoInteger(ACCOUNT_LOGIN);
   double balance = AccountInfoDouble(ACCOUNT_BALANCE);
   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   
   datetime fromDate = TimeCurrent() - (InpDaysBack * 86400);
   datetime toDate = TimeCurrent() + 86400;
   
   if(!HistorySelect(fromDate, toDate))
   {
      Print("[-] Khong lay duoc lich su lenh MT5!");
      return;
   }
   
   int totalDeals = HistoryDealsTotal();
   int newDeals = 0;
   int skippedDeals = 0;
   
   string url = "https://crypto-journal-twhs.onrender.com/api/mt5/webhook";
   string headers = "Content-Type: application/json\r\n";
   
   PrintFormat("[*] Tim thay %d ban ghi lich su tu MT5. Dang dong bo...", totalDeals);
   
   for(int i = 0; i < totalDeals; i++)
   {
      ulong ticket = HistoryDealGetTicket(i);
      if(ticket <= 0) continue;
      
      long entry = HistoryDealGetInteger(ticket, DEAL_ENTRY);
      // Chi lay cac deal dong lenh (DEAL_ENTRY_OUT hoac DEAL_ENTRY_INOUT)
      if(entry != DEAL_ENTRY_OUT && entry != DEAL_ENTRY_INOUT) continue;
      
      string symbol = HistoryDealGetString(ticket, DEAL_SYMBOL);
      if(StringLen(symbol) == 0) continue;
      
      long dealType = HistoryDealGetInteger(ticket, DEAL_TYPE);
      string typeStr = (dealType == DEAL_TYPE_BUY) ? "BUY" : "SELL";
      double price = HistoryDealGetDouble(ticket, DEAL_PRICE);
      double profit = HistoryDealGetDouble(ticket, DEAL_PROFIT);
      double volume = HistoryDealGetDouble(ticket, DEAL_VOLUME);
      datetime dealTime = (datetime)HistoryDealGetInteger(ticket, DEAL_TIME);
      string timeStr = TimeToString(dealTime, TIME_DATE|TIME_SECONDS);
      
      // Tao JSON payload
      string jsonPayload = StringFormat(
         "{\"login\":\"%d\",\"server\":\"%s\",\"ticket\":\"%d\",\"deal_id\":\"%d\","
         "\"type\":\"%s\",\"symbol\":\"%s\",\"entry_price\":%f,\"exit_price\":%f,"
         "\"profit\":%f,\"volume\":%f,\"balance\":%f,\"equity\":%f,\"close_time\":\"%s\",\"open_time\":\"%s\"}",
         login, server, ticket, ticket,
         typeStr, symbol, price, price,
         profit, volume, balance, equity, timeStr, timeStr
      );
      
      char postData[];
      char resultData[];
      string resultHeaders;
      StringToCharArray(jsonPayload, postData, 0, WHOLE_ARRAY, CP_UTF8);
      ArrayResize(postData, ArraySize(postData) - 1);
      
      ResetLastError();
      int res = WebRequest("POST", url, headers, 10000, postData, resultData, resultHeaders);
      if(res == 201)
      {
         newDeals++;
         PrintFormat("[+] THEM MOI: %s %s | PnL: $%.2f | Ve #%d", symbol, typeStr, profit, ticket);
      }
      else if(res == 200)
      {
         skippedDeals++;
      }
      else if(res == -1)
      {
         PrintFormat("[-] Loi WebRequest (Ma loi %d). Vui long bat WebRequest trong MT5 (Tools -> Options -> Expert Advisors) va them URL: %s", GetLastError(), url);
         break;
      }
   }
   
   Print("==================================================");
   PrintFormat("[v] HOAN TAT! Lenh moi: %d | Lenh cu da co: %d", newDeals, skippedDeals);
   PrintFormat("[v] So du cap nhat: $%.2f", balance);
   Print("==================================================");
}
