Search.setIndex({docnames:["access","accounts","analysis","arbitration","basic","bbands","combined","comdirect_status_report","comdirect_status_update","config","constants","data_access","depots","example","index","lstm","macd","macd_advanced","messages","modules","orders","performance_simulation","preprocessing","print_table","rsi_ema","rsi_sma","run_analysis","session"],envversion:{"sphinx.domains.c":2,"sphinx.domains.changeset":1,"sphinx.domains.citation":1,"sphinx.domains.cpp":4,"sphinx.domains.index":1,"sphinx.domains.javascript":2,"sphinx.domains.math":2,"sphinx.domains.python":3,"sphinx.domains.rst":2,"sphinx.domains.std":2,"sphinx.ext.intersphinx":1,sphinx:56},filenames:["access.rst","accounts.rst","analysis.rst","arbitration.rst","basic.rst","bbands.rst","combined.rst","comdirect_status_report.rst","comdirect_status_update.rst","config.rst","constants.rst","data_access.rst","depots.rst","example.rst","index.rst","lstm.rst","macd.rst","macd_advanced.rst","messages.rst","modules.rst","orders.rst","performance_simulation.rst","preprocessing.rst","print_table.rst","rsi_ema.rst","rsi_sma.rst","run_analysis.rst","session.rst"],objects:{"":[[14,0,0,"-","example"]],"automation.comdirect_status_report":[[7,1,1,"","create_page"]],"src.analysis":[[2,2,1,"","Analysis"]],"src.analysis.Analysis":[[2,3,1,"","analysis_length_post"],[2,3,1,"","analysis_length_pre"],[2,4,1,"","analyze"],[2,4,1,"","calc_parameters"],[2,3,1,"","decision"],[2,3,1,"","display_analysis"],[2,3,1,"","logger_name"],[2,3,1,"","ohlc_data"],[2,3,1,"","prediction_length"],[2,3,1,"","save_analysis"],[2,3,1,"","sequence_length"],[2,3,1,"","symbol"]],"src.data_access":[[11,2,1,"","DataAccess"]],"src.data_access.DataAccess":[[11,4,1,"","access_alphavantage"],[11,3,1,"","access_config"],[11,3,1,"","access_userdata"],[11,3,1,"","adjusted"],[11,3,1,"","data_json"],[11,3,1,"","data_pandas"],[11,4,1,"","dict_to_pandas_alphavantage"],[11,3,1,"","end"],[11,3,1,"","period"],[11,3,1,"","source"],[11,3,1,"","start"],[11,3,1,"","ticker"],[11,3,1,"","ticker_name"],[11,3,1,"","type_series"],[11,4,1,"","update_values"]],"src.lib":[[9,0,0,"-","config"],[18,0,0,"-","messages"],[23,0,0,"-","print_table"]],"src.lib.config":[[9,2,1,"","Config"]],"src.lib.config.Config":[[9,3,1,"","filename"],[9,4,1,"","get_dictonary"],[9,3,1,"","json_data"],[9,3,1,"","json_file"],[9,4,1,"","load_config"],[9,4,1,"","load_config_file"]],"src.lib.invst_const":[[10,0,0,"-","constants"]],"src.lib.messages":[[18,1,1,"","get_status"]],"src.lib.print_table":[[23,1,1,"","summary_table"]],"src.lib_analysis":[[3,0,0,"-","arbitration"],[4,0,0,"-","basic"],[21,0,0,"-","performance_simulation"],[22,0,0,"-","preprocessing"]],"src.lib_analysis.arbitration":[[3,2,1,"","Arbitration"]],"src.lib_analysis.arbitration.Arbitration":[[3,4,1,"","arbitrate"],[3,4,1,"","define_actions"],[3,4,1,"","recommend_threshold_cross"],[3,4,1,"","recommend_threshold_curve"]],"src.lib_analysis.basic":[[4,2,1,"","Basic"]],"src.lib_analysis.basic.Basic":[[4,4,1,"","calc_EMA"],[4,4,1,"","calc_MovingStdDev"],[4,4,1,"","calc_SMA"],[4,4,1,"","calc_absolute"],[4,4,1,"","calc_change"],[4,4,1,"","calc_delta"],[4,4,1,"","calc_difference"],[4,4,1,"","calc_division"],[4,4,1,"","calc_integration"],[4,4,1,"","calc_maximum"],[4,4,1,"","calc_minimum"],[4,4,1,"","calc_multiplication"],[4,4,1,"","calc_scalar_multiplication"],[4,4,1,"","calc_threshold"],[4,4,1,"","convert_numpy"],[4,4,1,"","split_data"]],"src.lib_analysis.methods":[[5,0,0,"-","bollinger_band"],[6,0,0,"-","combined"],[15,0,0,"-","lstm"],[16,0,0,"-","macd"],[24,0,0,"-","rsi_ema"],[25,0,0,"-","rsi_sma"]],"src.lib_analysis.methods.bollinger_band":[[5,2,1,"","BOLLINGER_BANDS"]],"src.lib_analysis.methods.bollinger_band.BOLLINGER_BANDS":[[5,4,1,"","calc_BBANDS"]],"src.lib_analysis.methods.combined":[[6,2,1,"","CombinedStrategy"]],"src.lib_analysis.methods.combined.CombinedStrategy":[[6,4,1,"","calc_CombinedStrategy"]],"src.lib_analysis.methods.lstm":[[15,2,1,"","LSTM"]],"src.lib_analysis.methods.lstm.LSTM":[[15,4,1,"","calc_LSTM"],[15,4,1,"","create_dataset"],[15,4,1,"","create_future_index"],[15,4,1,"","create_lstm_model"],[15,4,1,"","squash_output"]],"src.lib_analysis.methods.macd":[[16,2,1,"","MACD"]],"src.lib_analysis.methods.macd.MACD":[[16,4,1,"","calc_MACD"]],"src.lib_analysis.methods.rsi_ema":[[24,2,1,"","RSI_EMA"]],"src.lib_analysis.methods.rsi_ema.RSI_EMA":[[24,4,1,"","calc_RSI_EMA"]],"src.lib_analysis.methods.rsi_sma":[[25,2,1,"","RSI_SMA"]],"src.lib_analysis.methods.rsi_sma.RSI_SMA":[[25,4,1,"","calc_RSI_SMA"]],"src.lib_analysis.performance_simulation":[[21,2,1,"","PerformanceSimulation"]],"src.lib_analysis.performance_simulation.PerformanceSimulation":[[21,4,1,"","calculate_reference"],[21,4,1,"","simulate_performance"]],"src.lib_analysis.preprocessing":[[22,2,1,"","PreProcessing"]],"src.lib_analysis.preprocessing.PreProcessing":[[22,4,1,"","define_closure"],[22,4,1,"","define_past_time"],[22,4,1,"","extend_time_range"],[22,4,1,"","truncate_range"]],"src.lib_comdirect":[[0,0,0,"-","access"],[1,0,0,"-","accounts"],[12,0,0,"-","depots"],[20,0,0,"-","orders"]],"src.lib_comdirect.access":[[0,2,1,"","Access"]],"src.lib_comdirect.access.Access":[[0,4,1,"","connect"],[0,4,1,"","revoke_token"]],"src.lib_comdirect.accounts":[[1,2,1,"","Accounts"]],"src.lib_comdirect.accounts.Accounts":[[1,4,1,"","get_accounts_balance"]],"src.lib_comdirect.depots":[[12,2,1,"","Depots"]],"src.lib_comdirect.depots.Depots":[[12,4,1,"","get_depot_position"],[12,4,1,"","get_depots"]],"src.lib_comdirect.orders":[[20,2,1,"","Orders"]],"src.lib_comdirect.orders.Orders":[[20,4,1,"","make_order"]],"src.session":[[27,2,1,"","Session"]],"src.session.Session":[[27,4,1,"","get_challenge_info"],[27,4,1,"","get_request_id"],[27,4,1,"","get_session_id"]],automation:[[14,0,0,"-","comdirect_status_report"],[14,0,0,"-","comdirect_status_update"],[26,0,0,"-","run_analysis"]],src:[[2,0,0,"-","analysis"],[11,0,0,"-","data_access"],[27,0,0,"-","session"]]},objnames:{"0":["py","module","Python module"],"1":["py","function","Python function"],"2":["py","class","Python class"],"3":["py","attribute","Python attribute"],"4":["py","method","Python method"]},objtypes:{"0":"py:module","1":"py:function","2":"py:class","3":"py:attribute","4":"py:method"},terms:{"0":[2,4,7,14,15,16,22],"00":14,"003b":[],"01":14,"02":14,"03":14,"04":14,"05":14,"06":14,"07":14,"08":14,"09":14,"095":14,"1":[2,3,4,5,6,7,14,15,16,18,24,25],"10":[3,14],"100":[15,24,25],"11":14,"12":[14,16],"127":[7,14],"13":14,"14":[14,24,25],"145":14,"146":14,"15":14,"16":14,"17":14,"18":14,"19":14,"2":[3,4,5,6,14,15,16],"20":[5,14],"2021":14,"21":14,"22":14,"2217071":14,"2262683":14,"2264406":14,"23":14,"2303091":14,"2328018":14,"24":14,"245":14,"25":14,"250":22,"2560270":14,"26":[14,16],"2689434":14,"29":14,"2929719":14,"2991297":14,"3":[15,18],"30":[14,24,25],"3034488":14,"3236288":14,"3265557":14,"3320536":14,"3338":14,"3389":14,"3393":14,"34":14,"3410":14,"3423":14,"3427":14,"3437":14,"3441":14,"3443":14,"3443000":14,"3444":14,"3447":14,"3455":14,"3460":14,"3463":14,"3466":14,"3467":14,"3469":14,"3472":14,"3473":14,"3482":14,"3483":14,"3485":14,"3492":14,"3495":14,"35":14,"3501":14,"3504":14,"3507":14,"3508":14,"3513":14,"3515":14,"3518":14,"3523":14,"3525":14,"3527":14,"3531":14,"3536":14,"3537":14,"3539":14,"3540":14,"3543":14,"3545":14,"3547":14,"3549":14,"3559":14,"3561":14,"3562":14,"3563":14,"3564":14,"3566":14,"3567":14,"3572":14,"3576":14,"3580":14,"3585":14,"3587":14,"3593":14,"3596":14,"36":14,"360":22,"3602":14,"3605":14,"3613":14,"3621":14,"3633":14,"3675":14,"3676":14,"3692246":14,"3696":14,"37":14,"3704":14,"3712":14,"3713":14,"3756995":14,"3762":14,"377":14,"39":14,"3d":15,"4":[14,15],"4001107":14,"4027422":14,"4035550":14,"41":14,"42":14,"425":14,"4294922":14,"45":14,"455":14,"47":14,"4847850":14,"4946203":14,"5":15,"50":14,"54":14,"56":14,"57":14,"5703538":14,"58":[],"6":15,"60":14,"64":14,"644":14,"67":14,"68":14,"69":14,"7":15,"70":[14,24,25],"71":14,"72":14,"726":14,"75":14,"77":14,"78":[],"79":14,"8050":[7,14],"81":14,"85":14,"865":14,"87":14,"88":14,"9":16,"91":14,"98":[],"99":14,"abstract":18,"boolean":2,"break":15,"case":[5,13,14,15,16,18,22],"class":[0,1,2,3,4,5,6,9,11,12,15,16,20,21,22,24,25,27],"default":[13,14,15,18],"export":[7,14,19],"final":[2,3,4,5,11,14,15,16,22],"float":[2,3,4,15,21],"function":3,"import":[14,15],"int":[2,4,15,22],"long":19,"new":[4,5,14,15,22],"return":[1,2,3,4,5,9,11,12,13,14,15,18,22],"short":[14,19],"true":[2,3,11,15,24,25],"try":[13,14,15],"while":[14,15,16,18],A:[2,3,6,11,14,15],As:[14,15],At:9,By:[13,14,18],For:[2,4,5,7,11,13,14,15,18,24,25],If:[4,15,24,25],In:[14,18],It:[4,14,15],No:22,Of:14,One:[],The:[2,3,4,5,6,7,9,11,13,14,15,16,18,22,24,25],There:18,These:[24,25],To:[3,6,11,15],_:15,__name__:7,aa:[],aaaa:[],ab:3,abl:14,about:3,abov:[4,5,14,24,25],absolut:[2,3,6],access:[7,13,19,27],access_alphavantag:11,access_config:[11,27],access_userdata:[11,27],accord:18,account:[13,15,19,22,27],account_numb:14,aces:11,acquir:14,acriv:14,acronym:[2,11],across:9,action:[3,14],activ:14,actual:14,ad:[4,5,14,15,22],add:[4,14,18],addit:[14,15],address:[7,14],adequ:[2,14,22],adjust:[2,5,11,14],adopt:14,advantag:14,after:[2,9,14,15],afterward:2,aggreg:14,aim:14,al:2,algo:[],algorithm:[14,15],align:[],all:[1,2,3,11,12,13,14,15,22],alloc:15,along:18,alpha:16,alphavantag:[13,14,19],alreadi:[4,5],also:[14,15],although:14,alwai:[14,15,22],amount:[11,14,22],amzn:14,an:[2,3,5,11,13,15,18,24,25],analys:14,analysi:[3,5,13,14,22,24,25,26],analysis_length:2,analysis_length_post:2,analysis_length_pr:2,analysis_result:2,analyz:[2,3],ani:[7,14,22,24,25],anoth:14,anti:15,api:[11,13,14,22],apikei:[11,14],app:7,appli:[2,5,14],applic:[7,9,15,16,24,25],approach:14,ar:[2,3,4,5,7,9,11,13,14,15,18,22,24,25],arbitr:[2,5,6,14,16,19,24,25],architectur:15,arima:[],around:14,arrai:15,asset:7,attent:22,attribut:2,authent:14,author:14,autom:[7,13],automat:[3,7,14,18],avail:[2,4,5,13,14,15,22],averag:[3,4,5,6,14,15,19,24,25],averagegain:[3,6],averageloss:[3,6],balanc:[1,14],band:[14,19,24,25],base:[0,1,2,3,4,5,6,7,9,11,12,14,15,16,20,21,22,24,25,27],basic:[2,5,6,14,15,16,19,24,25],bat:14,bband:5,becom:15,been:[],befor:[14,15],begin:16,below:[3,4,6,11,14,15,18,24,25],benefit:[2,14],besid:14,better:[2,3,6],between:[2,3,4,6,14,15],bigger:14,bin:14,block:[9,14,15],bmatrix:[],bolling:[14,19],bollinger_band:[2,5],bool:[2,3,11,15],both:[3,6,14,24,25],bring:2,broker:[],bui:[2,3,5,6,16,24,25],build:14,bullish:[3,6],calc_absolut:4,calc_bband:5,calc_chang:4,calc_combinedstrategi:6,calc_delta:4,calc_differ:4,calc_divis:4,calc_ema:4,calc_integr:4,calc_lstm:15,calc_macd:16,calc_macd_advanc:[],calc_maximum:4,calc_minimum:4,calc_movingstddev:4,calc_multipl:4,calc_paramet:2,calc_rsi_ema:24,calc_rsi_sma:25,calc_scalar_multipl:4,calc_sma:4,calc_threshold:4,calcul:[2,3,4,5,6,15,16,24,25],calculate_refer:21,call:[4,7,9,15],can:[2,3,6,7,13,14,15,22,24,25],capac:14,care:[24,25],cell:15,center:[],central:18,cfg:14,chanc:15,chang:[2,4,14],chart:[2,7,14],chosen:14,clear:18,client:14,client_id:14,client_secret:14,close:[4,5,11,14,15,16,22,24,25],closennvalu:14,closevalu:[],closevalue_:[24,25],closevalue_n:[24,25],closur:[5,11,22],code:15,coeffici:11,collect:[7,14],color:15,column:[2,3,4,5,15,22],combin:[2,3,14,15,19],combinedstrategi:[2,6],comdirect:[8,13,14,19],comdirect_status_report:19,comdirect_status_upd:19,command:14,commmand:14,common:14,commplex:14,compar:[3,6],comparison:[2,4],complet:[2,4,9,11,14],complex:[3,6,14],compon:14,compos:11,comput:14,config:[9,11],configur:[11,13,14,19,22,23],connect:0,consecut:[2,24,25],consider:2,consist:14,consol:[7,13,14,18,23],constant:19,contain:[3,14],content:[9,13,18],converg:[14,19],convert:[11,18],convert_numpi:4,core:[2,3,4,14,15,21],correct:[14,22],could:[14,24,25],cours:14,cover:14,crash:[2,3],creat:[13,14,15,23],create_dataset:15,create_future_index:15,create_lstm_model:15,create_pag:7,creation:14,cross:3,crypto:14,cryptocurr:14,css:7,current:[0,5,8,13,14,16],cut:15,dai:[3,4,6,11,13,14,15,22,24,25],daili:11,dash:[7,14],data:[3,4,5,6,7,13,15,19,22],data_access:[11,14],data_json:11,data_panda:11,data_sourc:11,data_source_access_data:11,data_source_nam:11,data_source_user_data:11,dataaccess:11,databas:14,datafram:[2,3,4,5,11,14,15,21,22],dataset:[2,15,22],date:[11,13,14,15,22],datetim:11,de:[4,5,16,24,25],deactiv:14,debug:[13,14,18],decid:14,decis:2,defin:[2,5,15,16,22],define_act:3,define_closur:22,define_past_tim:22,defini:14,definit:18,delai:14,delimchar:[],delta:[3,4,6],demand:15,demonstr:14,denot:15,depend:[3,4,13,14,15,22],depot:[13,14,19,27],depot_id:12,describ:18,descript:2,design:[9,14,15],desir:14,detail:[13,14,15],determin:[2,16,24,25],deviat:[4,5],diagon:15,dict_to_pandas_alphavantag:11,dictionari:[2,9,11,13,14,18],difer:[],diffeenrc:[24,25],differ:[2,3,4,6,13,14,15,22],differenti:4,dimens:15,directli:[14,22],displai:[2,7,13,14,18,19],display_analysi:2,diverg:[14,19],dividend:[4,11],dividend_column:4,divis:[4,15],divisor:4,divisor_column:4,doc:14,document:[13,15],doesn:2,done:[3,6,13,14,15,22],down:2,downsid:2,downtrend:[24,25],drop:[3,24,25],due:[14,15],dure:[13,14,24,25],e:[3,6,13,14,15,24,25],each:[2,13,14,15],either:[13,14],element:[13,14,15,18],ema:[4,19],ema_:16,empir:[3,6],enabl:15,encapsul:14,end:[11,16],entri:[2,3,4,5,11,15,18,22,24,25],enumer:2,environmenet:14,environmnet:14,epoch:15,equal:[4,14,15],error:18,especi:14,etc:11,etf:14,evalu:[7,14,23,26],even:15,event:5,eventu:22,everi:4,evolut:14,exampl:[4,7,11,15,18,19,22,24,25],exce:[24,25],excel:[7,8,13,14,23],excel_filenam:23,exchang:14,execut:[2,7,13],expect:[4,5,11,14],explicitli:[2,4,5],exponenti:[4,16,24,25],export_comdirect_:[7,14],extend:14,extend_original_data:15,extend_time_rang:22,extens:14,extrapol:14,factor1_column:4,factor2:4,factor2_column:4,factor:[4,14],fail:18,fall:[24,25],fals:[2,15],far:15,fast:14,featur:[14,15],fetch:[11,13],few:14,figur:14,file:[7,8,9,13,14,18],filenam:[9,13,14],filter:14,first:[3,5,6,11,13,14,15,23],fix:[14,22],flag:18,fo:22,focu:2,folder:[7,13,14],follow:[2,11,13,14,15,16,18,22,24,25],format:[4,9,23],former:14,formular:16,forna:14,forward:14,frac:[3,5,6,16,24,25],frame:[2,3,4,11,15,21],framework:14,frequenc:14,frequent:[24,25],from:[2,3,4,5,6,8,11,12,13,15,16,18,22,23,24,25],full:11,fund:14,further:14,futur:[15,22],g:[3,6,13,14,15,24,25],gain:[3,6,14,24,25],gener:[2,14,18],get:[8,14,18],get_accounts_bal:1,get_challenge_info:27,get_depot:12,get_depot_posit:12,get_dictonari:9,get_request_id:27,get_session_id:27,get_statu:18,given:[11,14,15,18,21],go:14,goal:[],goog2:[13,14],goog:11,googl:11,google_data:11,graphic:14,greater:15,guidelin:[24,25],ha:[14,15,24,25],handl:[14,18],have:[2,13,14,15,18,22],header:11,help:[24,25],here:[9,14,15],hidden_neuron:15,high:[2,11,14],higher:[2,3],highest:15,hipotet:[],histeresi:[3,24,25],histogram:[14,16],histor:11,historgram:[],histori:[],hit:[24,25],hold:[2,3,5,6],holidai:[15,22],how:14,howev:[2,14,15,22,24,25],html:14,http:[7,14],hysteresi:3,i:[5,15],id:[14,18],identifi:18,ignor:[7,14],illustr:[14,15],imag:14,immediatelli:2,impact:14,implement:[14,15],improv:[2,14,23,24,25],incid:15,includ:[22,24,25],inclus:2,increas:15,increment:[15,22],independ:14,index:[14,15,19,22],indic:[2,3,5,15,16,24,25],individu:[2,14],inertia:14,info:[13,14,18,27],inform:[4,7,9,12,13,14,18,22,24,25],initi:[2,9,14,15,22],initial_valu:[2,21],inlin:[],input:[2,3,4,5,11,13,14,15,22],input_sequence_length:15,insid:15,instal:14,instanc:14,instead:22,instruct:14,integ:15,integer:2,integr:4,intend:[14,18,22],interpret:[16,24,25],introduc:3,invalid:[13,14],investi:14,investopedia:[24,25],issu:14,item:11,iter:15,its:[9,13,14,15],itself:[3,6,14],json:[9,11,13,14],json_data:9,json_fil:9,just:[14,15],k:[5,16],keep:[9,14,22],kei:[11,14],known:14,l:15,label:15,larger:2,last:[5,14,15,24,25],later:14,latest:22,lb:5,ldot:15,learn:[2,3,6,14,15],least:14,left:[5,15],length:[4,5,14,15,16,22],less:15,level:[13,14,15,18],lib:[9,18,23],lib_analysi:[2,3,4,5,6,15,16,21,22,24,25],lib_comdirect:[0,1,12,20,27],librari:[14,18],like:14,limit:[3,6,14,22],line:[16,24,25],linear:15,linux:14,list:[13,14,15,22,26],load:[7,9,13,14,15],load_config:9,load_config_fil:9,log:[13,14,18],logger:[2,9,13,14,18],logger_nam:[2,9,11,18,27],logic:[3,6],longer:[],lose:[3,6],loss:[3,6,14,24,25],low:[11,14],lower:[3,5,24,25],lstm:[2,16,19],m:14,macd:[2,3,6,14,19],macd_advanc:[],macdadvanc:[],machin:[3,6],magnitud:16,mai:[2,24,25],major:14,make:[7,14,22],make_ord:20,manag:[14,19],mani:[3,6,14,15],market:[],match:[7,11,14],math:[],mathemat:14,matrix:[],maximum:4,mean:[2,5,14,24,25],measn:[24,25],memori:19,messag:19,message_id:18,method:[2,3,5,6,7,9,11,14,15,16,18,22,24,25],methodolog:14,metric:14,microsoft:[13,14],micrsoft:14,might:[14,22],mind:14,minimum:4,minimum_length:4,minu:4,minuend:4,minuend_column:4,miss:14,mode:[3,15],model:[14,15],modul:[2,9,14,18,19],momentum:14,monthli:11,more:[3,13,14,15,24,25],most:[3,15],mostli:14,move:[4,5,14,15,19,24,25],movement:[2,3,6,15],much:14,multipl:4,must:[11,14,18],n:[5,15,16,24,25],name:[2,3,4,5,6,9,11,14,15,16,18,22,24,25],name_of_virtualenv:14,nan:4,necessari:[2,7,14,15,22],need:[7,14,24,25],neg:[2,3,6,16],netowork:[2,14],network:[2,14,15],neural:[2,14,15],neutral:18,next:[13,14,15,22],nn:14,none:[2,3,4,5,9,11,18,21,22],norm:3,normal:[3,15],note:[14,15],np:15,number:[2,4,14,15,22,24,25],number_block:15,number_featur:15,numer:15,numpi:15,numpy_data:[],object:[0,1,3,4,9,11,12,20,21,22],observ:[3,6,14],obtain:14,obtanin:14,off:14,ohlc:[2,11,14],ohlc_data:2,ohlc_dataset:[2,22],ohlc_dataset_predict:22,older:2,onc:14,one:[2,4,5,13,14,15,22],ones:[24,25],onli:[3,7,14,15,18,22],open:[4,11,14],oper:[2,5,15,19,22],operation_cost:[2,21],opposit:[24,25],optim:15,option:[3,4,11,15,18,21],optmiz:14,order:[3,18,19,27],organ:14,origin:[4,14],other:[2,3,6,7,9,13,14],othernnsourc:14,otherwis:[4,11],out:14,outcom:[2,4,5,14],output:[2,14,15],output_sequence_length:15,outsid:22,over:[3,6,24,25],overal:[3,6,14,26],overbought:[5,14,24,25],overlap:15,overlin:5,oversold:[5,14,24,25],overview:13,own:14,packag:14,page:[],pair:15,panda:[2,3,4,5,11,14,15,21,22,23],param:18,paramet:[3,4,5,9,11,14,15,18,22],pars:[7,9,14],part:[9,15],pass:[2,4,7,9,15,18],path:[9,14],pathlib:9,pattern:[7,14],peak:3,per:[13,14,15],percetage_learn:4,perfom:21,perform:[2,3,6,13,14,19,26],performance_simul:[5,6,16,21,24,25],performancesimul:[5,6,16,21,24,25],period:[3,6,11],permit:14,physic:14,pictur:15,pin:14,pip:14,place:14,placement:14,platform:14,pleas:14,plot:15,plotli:[7,14],plural:14,point:[14,15],popul:22,posit:[2,3,6,12,14,16],possibl:[3,14,15,18],potenti:[14,24,25],powershel:14,pre:[2,14,19],predict:[2,14,15,22],prediction_length:[2,15],preprocess:[2,22],presenc:14,present:[13,14,15,23],previou:[3,5,6,14,15,24,25],previous_dai:15,price:[4,13,14,22,24,25],pricipl:14,print_tabl:23,prioriti:3,process:[2,14,19],produc:[3,6,13,14],product:14,project:13,proper:[14,22],properli:14,propos:18,protect:3,provid:[14,15,26],purchas:[13,14],pure:[3,6],purpos:[13,14],py:[18,19],pytest:14,python3:14,python:[14,18],r:14,ralli:[24,25],ran:14,rang:[15,22,24,25],rare:[24,25],rate:14,ratio:[2,3,6],ratio_train:15,reach:[24,25],read:[24,25],real:22,rearrang:15,reason:15,receiv:22,recent:3,recommand:5,recommend:[3,5,9,14,16],recommend_threshold_cross:3,recommend_threshold_curv:3,recur:16,recurr:[14,15],refer:[5,11,16],reference_column_low:3,reference_column_upp:3,regular:[11,14],rel:[3,6,14,19],relat:14,relev:[15,22],reli:14,rell:[],remain:15,rephas:15,replac:[4,14],replacd:14,replace_valu:4,replic:14,report:[7,14,26],report_analysi:[5,6,16,24,25],reportanalysi:[5,6,16,24,25],repres:[3,11,15],represenst:5,requir:14,respect:[5,15],respond:14,respons:[11,14],result:[2,3,4,5,6,7,11,13,15,16,21,22,24,25,26],result_column:[3,4,15,21],result_datafram:[3,4,21],results_summari:23,retriev:11,revers:[15,24,25],revok:0,revoke_token:0,right:[5,15],rightarrow:15,risk:14,rnn:[2,14,15],roll:4,root:14,row:[],rs:[24,25],rsi:[3,6,14,19],rsi_ema:[2,24],rsi_sma:[2,25],rule:5,run:[2,14,15],run_analysi:19,s:[13,15,18],same:[4,5,9,14,15,23],sampl:[2,4,5,15],save:[2,13,14],save_analysi:2,save_model:15,scalar:4,script:[7,8,14,26],se:15,search:14,second:[11,14,15,23],secret:14,section:14,see:[11,13,14,15,24,25],seem:[3,6],self:16,sell:[2,3,5,16,24,25],separ:[13,14],seq:15,sequenc:[2,13,14,15,22,26],sequence_length:[2,4,15],seri:[2,3,4,11,15,22],server:[7,14],session:[0,14,19],set:[14,18],shall:14,shape:15,sheet:[13,14,23],shift:4,shift_futur:15,shift_last:22,shorter:14,should:[2,14,22,24,25],shouldn:2,show:14,sign:[],signal:[2,14,16],similar:14,similarli:5,simpl:[4,5,14,15,24,25],simul:[2,5,19],simulate_perform:21,sinc:[2,13,14,15,22],singl:[3,9,15,18],situat:5,size:15,skip:[15,22],sma20:[],sma:[4,5,19],sma_:5,so:[3,7,9,13,14,15,22,24,25],sourc:[3,6,11,14,22],source_column:[3,4,15],source_column_clos:21,source_column_decis:21,source_column_ev:21,specifi:[4,11],sphinx:14,split:[11,14,15],split_data:4,spot:[24,25],sqrt:5,squash:15,squash_output:15,src:[0,1,2,3,4,5,6,9,11,12,14,15,16,18,20,21,22,23,24,25,27],stai:[24,25],standard:[4,5],start:[11,14,15],state:[3,6],statu:[13,18],stddev:5,stddev_:5,step:[2,13,14,15,16,24,25],still:14,stock:[3,6,14,16],stopgain:[2,21],stoploss:[2,21],store:[4,7,8,9,11,13,14,15,18],storrag:[13,14],str:[2,3,4,15,21],straight:14,strategi:[2,3,5,13,19,21],strength:[14,19],string:[2,3,4,9,11,14,15,18],strong:[3,6],stronger:14,structur:[14,15],strucutr:15,sub:[9,15],subseq:15,subtrahend:4,subtrahend_column:4,succes:14,success:[14,15,18],successfu:14,suggest:14,sum:[2,3,6,15],sum_:5,summari:[2,5,6,16,19,24,25],summary_t:23,suppli:[14,15],support:[2,13,14,18],sure:14,swing:[24,25],symbol:[2,3,6,13,14,26],sysmbol:[],system:14,t:[2,24,25],tag:[14,22],take:[2,3,5],taken:[5,13,14,15,22,24,25],target:14,tax_percentag:[2,21],techniqu:2,templat:[11,14],tend:[14,24,25],tensor:15,term:[14,19],termin:14,test:15,test_access:14,text:[15,16,18],than:[3,15],thei:14,them:[2,4,7,14],themselv:2,thenvolum:14,thi:[2,3,4,5,7,11,14,15,18,22,24,25],this_:[],threshold:[3,4],threshold_low:3,threshold_upp:3,thu:[5,15],ticker:[2,3,4,11,13,14,26],ticker_nam:11,ticket:[],time:[2,11,14,15],time_step:15,timedelta64:15,timedelta:15,timeseri:11,todai:11,token:0,too:2,tool:[14,24,25],total:3,toward:14,track:[13,14,15],tracker:[8,14],trade:14,trader:14,train:15,trend:[24,25],tri:[14,15],trigger:3,trim:22,truncat:[2,22],truncate_rang:22,tupl:[3,18],two:[13,14],txt:14,type:[2,4,5,9,11,14,15,22],type_seri:11,u:[],ub:5,ultim:14,unabl:[24,25],underbrac:[],undercbrac:[],uniqu:15,up:[2,11,14,18],updat:[9,11],update_valu:11,upper:[3,5],upsid:[24,25],uptrend:[24,25],upward:[3,6],us:[2,3,4,5,6,8,9,11,13,15,16,18,22,24,25],usag:11,user:[11,13,14,18,23],user_data:[11,14],valid:[3,11,13,14],valu:[2,3,4,5,6,8,9,11,13,14,15,16,24,25],value_predict:4,valueclosure_:[],values_upper_mid_low:3,vanilla:14,vc:[5,16],vc_:5,vector:15,venv:14,verbos:15,veri:14,verifi:[11,14],version:[14,23],virtualenv:14,volum:[11,14],wai:[14,24,25],warn:18,we:15,weaken:[24,25],websit:14,week:14,weekend:[15,22],weight:15,weighted_averag:[],weigth:15,were:14,when:[2,3,5,14,24,25],whenev:14,where:[3,5,6,9,11,13,14,15,16,18,24,25],which:[2,3,4,5,6,7,9,11,14,15,18,22],whilst:[13,14],width:[],window:[4,14],without:14,work:22,would:15,written:15,x:[15,16],x_:15,xlsx:[13,14],y:15,year:22,yet:14,you:14,your:[11,14]},titles:["Access module","Accounts","Data Analysis","Arbitration","Basic operations","Bollinger Bands","Combined strategy","comdirect_status_report.py","comdirect_status_update.py","Configuration management","Constants","Data Access (AlphaVantage)","Depots","example.py","Welcome to INVST documentation!","LSTM (Long Short-Term Memory)","MACD (Moving Average Convergence Divergence)","MACD Advanced","Messages management","Core","Orders","Performance Simulation","Pre-Processing","Display and Export data (Analysis summary)","RSI EMA (Relative Strength Index)","RSI SMA (Relative Strength Index)","run_analysis.py","Trading session (Comdirect)"],titleterms:{"do":14,"export":23,"long":15,"short":15,To:14,access:[0,11,14],account:[1,14],advanc:17,alphavantag:11,amazon:14,an:14,analysi:[2,19,23],analyz:14,arbitr:3,autom:[14,19],averag:16,band:5,basic:4,bolling:5,broker:14,bui:14,combin:6,comdirect:27,comdirect_status_report:[7,14],comdirect_status_upd:[8,14],configur:9,constant:10,content:14,converg:16,core:19,data:[2,11,14,23],decis:14,depot:12,displai:23,diverg:16,document:14,ema:24,environ:14,exampl:[13,14],execut:14,fetch:14,from:14,futur:14,gener:19,goal:14,histori:14,hold:14,index:[24,25],indic:14,invst:14,librari:19,lstm:15,macd:[16,17],manag:[9,18],market:14,memori:15,messag:18,method:19,modul:0,move:16,oper:[4,14],order:[14,20],overview:14,packag:[],page:14,paramet:2,perform:21,pre:22,principl:14,process:22,project:14,py:[7,8,13,14,26],rel:[24,25],result:14,rsi:[24,25],run_analysi:[14,26],s:14,script:19,sell:14,seri:14,session:27,setup:14,simul:21,sma:25,statu:14,strategi:[6,14],strength:[24,25],summari:23,tabl:14,take:14,term:15,test:14,trade:[19,27],trader:19,unit:14,us:14,virtual:14,welcom:14,work:14}})