# 人臉識別點名

##主要架構

學生註冊系統
    用信箱驗證(與身分確認)		 
    	透過輸入學號來進行登入
    	輸入後會傳一次性密碼到mail做認證
    	上傳與刪除照片	
    	選擇課程	
		

老師系統(網站，應用程式)：
    登入、註冊(mail、帳號、密碼)
    課程設定(匯入選課名單(.xslx)、輸入課程名稱、課程編號)
    確認學生選擇狀況
    匯出點名紀錄(csv)   (應用程式才有)
    設定點名時間	(應用程式才有)
	

中間管理系統：              
    資料儲存(照片，特徵資料)
    預辨識
    中控系統


資料庫結構：
    學生資料 (Student)
    	學生ID
    	註冊時間
    	face

    修課狀況 (ClassToStudent)
    	課程ID
    	學生班級
    	學生ID	
    	學生姓名
    	註冊狀況(True, False)

    課程資料 (TeacherToClass)
    	課程ID
    	課程名稱
    	老師ID
		
    老師資料 (Teacher)
    	老師ID
    	密碼(雜湊碼)	
    	mail
	
    Student_Face
    	學生ID
    	照片ID
    	feature(陣列改成字串儲存)

    資料更新時間 (UpdataTime)
    	date


