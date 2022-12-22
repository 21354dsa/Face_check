
using MailKit.Net.Smtp;
using MailKit.Security;
using MimeKit;
using Newtonsoft.Json.Linq;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Net.Http;
using System.Text;
using System.Windows.Forms;
using System.Threading;

namespace TeacherApp
{

    public partial class Form2 : Form
    {
        TimeSpan t_strat;
        List<string> present_mail = new List<string>();
        string folderPath = $@"C:\Users\{Environment.UserName}\.FaceCheckIn";
        Process explorer = new Process();
        Form3 form3 = new Form3();
        JObject now_class;
        public void end_checkin()
        {
            timer1.Enabled = false;
            var values = new Dictionary<string, string>();
            values["response"] = "";
            values["Camera"] = "";
            setCamera(values);
            labExe.Text = "可進行點名";
            btn_start.Text = "開始點名";
        }

        public void comboUtil(JObject json)
        {
            comboBox1.Items.Clear();
            comboBox1.Items.Add("請選擇想查詢的課程");
            foreach (var class_obj in json["request"])
            {
                comboBox1.Items.Add(class_obj["number"] + " " + class_obj["name"]);
            }
            comboBox1.SelectedIndex = 0;
        }

        public void DownloadCSV(string fileName="test.csv")
        {
            
            if (!Directory.Exists(folderPath))
            {
                Directory.CreateDirectory(folderPath);
            }
            StringBuilder sb = new StringBuilder();


            for (int i = 0; i < listView1.Columns.Count; i++)
            {
                sb.Append(listView1.Columns[i].Text);
                if (i != listView1.Columns.Count - 1)
                {
                    sb.Append(",");
                }
            }
            
            foreach (ListViewItem item in listView1.Items)
            {
                sb.Append("\n");
                for (int i = 0; i < item.SubItems.Count; i++)
                {
                    sb.Append(item.SubItems[i].Text.ToString());
                    if (i != item.SubItems.Count - 1)
                    {
                        sb.Append(",");
                    }
                }
              
            }
            FileStream fs = null;
            fs = new FileStream(folderPath+"\\"+fileName, FileMode.OpenOrCreate);
            //建立StreamWriter，取得Response的OutputStream並設定編碼為UTF8
            StreamWriter sw = new StreamWriter(fs, Encoding.UTF8);
            //寫入資料
            
            sw.Write(sb.ToString());
            //關閉StreamWriter
            sw.Close();
            //釋放StreamWriter資源
            sw.Dispose();
            MessageBox.Show("匯出位置："+ folderPath + "\\" + fileName);
            MessageBox.Show("匯出成功");
        }

        private void ListView_search(String[] columns, JObject json)
        {
            now_class = json;
            listView1.Clear();
            for (int i = 0; i < columns.Length; i++)
            {
                listView1.Columns.Add(columns[i], 100);
            }
            if (columns.Length <= 3)
            {
                foreach (var stud_obj in json["request"])
                {
                    var item = new ListViewItem($"{stud_obj["studClass"]}");
                    item.SubItems.Add($"{stud_obj["studId"]}");
                    item.SubItems.Add($"{stud_obj["studName"]}");
                    listView1.Items.Add(item);
                }
            }
            else
            {
                foreach (var stud_obj in json["request"])
                {
                    var item = new ListViewItem($"{stud_obj["studClass"]}");
                    item.SubItems.Add($"{stud_obj["studId"]}");
                    item.SubItems.Add($"{stud_obj["studName"]}");
                    item.SubItems.Add($"{stud_obj["choose"]}");
                    listView1.Items.Add(item);
                }
            }
        }

        private void ListView_strat(JObject json)
        {
            //新增一欄點名用
            var values = new Dictionary<string, string>();
            present_mail.Clear();
            foreach (var item in json["request"])
            {
                present_mail.Add(item["studentId"].ToString());
            }

            //values["response"] = json["request"].ToString();

            FileStream fs = null;
            fs = new FileStream(".\\" + "stud_data.txt", FileMode.OpenOrCreate);
            //建立StreamWriter，取得Response的OutputStream並設定編碼為UTF8
            StreamWriter sw = new StreamWriter(fs, Encoding.UTF8);
            //寫入資料
            sw.Write(json["request"].ToString());
            //關閉StreamWriter
            sw.Close();

            values["webcamNumber"] = txtcam.Text;
            values["Camera"] = "1";
            setCamera(values);
        }   

        private async void setCamera(Dictionary<string, string> values)
        {
            using (HttpClient client = new HttpClient())
            {

                try
                {
                    string url = "http://127.0.0.1:3000/OpenCamera";
                    var data = new FormUrlEncodedContent(values);
                    var response = await client.PostAsync(url, data);
                    string result = response.Content.ReadAsStringAsync().Result;
                    JObject json = JObject.Parse(result);
                    if ((string)json["msg"] != "")
                    {
                        MessageBox.Show((string)json["msg"], "錯誤", MessageBoxButtons.OKCancel, MessageBoxIcon.Error);
                        end_checkin();
                    }
                }
                catch (Exception e) 
                {
                    MessageBox.Show("請檢察鏡頭是否連接", "錯誤", MessageBoxButtons.OKCancel, MessageBoxIcon.Error);
                    end_checkin();
                }
            }
        }

        private async void checkExe()
        {
            var values = new Dictionary<string, string>();
            values["response"] = "123";
            try
            {
                using (HttpClient client = new HttpClient())
                {
                    string url = "http://127.0.0.1:3000/checkExe";
                    HttpResponseMessage response = await client.GetAsync(url);
                    response.EnsureSuccessStatusCode();
                    string result = response.Content.ReadAsStringAsync().Result;
                    JObject json = JObject.Parse(result);
                    if ((bool)json["bool"] && Time_checkExe.Enabled)
                    {
                        btn_start.Enabled = true;
                        Time_checkExe.Enabled = false;
                        labExe.Text = "可以進行點名";
                        btn_start.Text = "開始點名";
                        form3.Visible = false;
                        //form3.Close();
                        //MessageBox.Show("啟動完畢可以進行點名");
                    }
                }
            }
            catch { }
        }

        public async void WebPost(Dictionary<string, string> values)
        {
            using (HttpClient client = new HttpClient())
            {
                String[] columns;
                string url = Class_constant.Url + "/api/" + values["Do"];
                var data = new FormUrlEncodedContent(values);
                var response = await client.PostAsync(url, data);
                string result = response.Content.ReadAsStringAsync().Result;
                JObject json = JObject.Parse(result);
                //MessageBox.Show(json.ToString());
                if ((bool)json["msg"]) { 
                    switch (values["Do"])
                    {
                        case "getClass":
                            comboUtil(json);
                            break;

                        case "getStudent":
                            columns = new string[] {"班級", "學號", "姓名", "註冊狀況" };                            
                            ListView_search(columns, json);
                            break;

                        case "getFeature":
                            ListView_strat(json);
                            break;
                    }
                }

            }
         
        }

        public async void SendAutomatedEmail(string To_name, string To_mail, BodyBuilder text, string who)
        {
            
            
            var message = new MimeMessage();
            message.From.Add(new MailboxAddress("臉部識別點名系統", "108406011@stud.sju.edu.tw"));
            message.To.Add(new MailboxAddress(To_name, To_mail));
            message.Subject = "臉部識別點名系統";

            message.Body = text.ToMessageBody();

            using (var client = new SmtpClient())
            {
                await client.ConnectAsync("smtp.gmail.com", 465, SecureSocketOptions.SslOnConnect).ConfigureAwait(false);
                client.Authenticate("project.test.22645@gmail.com", "eszgezutnqucqdno");
                try
                {
                    await client.SendAsync(message).ConfigureAwait(false);
                    await client.DisconnectAsync(true).ConfigureAwait(false);
                    if(who=="teacher")
                        MessageBox.Show("成功寄出");
                }
                catch (Exception ex)
                {
                    /*if (ex != null)
                    {
                        MessageBox.Show( ex.Message.ToString());
                    }
                    else
                    {
                        MessageBox.Show("不明錯誤。");
                    }*/
                }

            }

        }

        public Form2()
        {
            InitializeComponent();
        }

        private void button1_Click(object sender, EventArgs e)
        {
            if (listView1.Columns.Count > 4)
            {
                string caption = "切換顯示課程";
                string message = "是否儲存本次的點名結果";
                var result = MessageBox.Show(message, caption,
                                 MessageBoxButtons.YesNo,
                                 MessageBoxIcon.Question);
                if (result == DialogResult.Yes)
                {
                    DownloadCSV(labclass.Text);
                }
            }
            if (comboBox1.Text != "請選擇想查詢的課程") { 
                string class_id = comboBox1.Text.Split(' ')[0];
                var values = new Dictionary<string, string>();
                values["Do"] = "getStudent";
                values["class_id"] = class_id;
                WebPost(values);
                
                btn_mail.Enabled = false;
            }
        }
        private void btn_start_Click(object sender, EventArgs e)
        {
            
            if (comboBox1.Text != "請選擇想查詢的課程" && btn_start.Text== "開始點名")
            {
                if (listView1.Items.Count == 0)
                {
                    MessageBox.Show("請先點選學生查詢");
                    button1.Focus();
                    //button1_Click(sender, e);
                    return;
                }
                if (listView1.Columns[listView1.Columns.Count - 1].Text == "註冊狀況")
                {
                    string[] columns = new string[] { "班級", "學號", "姓名" };
                    ListView_search(columns, now_class);
                }
                
                btn_csv.Enabled = true;
                btn_mail.Enabled = true;
                string[] list = comboBox1.Text.Split(' ');
                string class_id = list[0];
                labclass.Text = list[0] + "_" + list[1] +
                                "_" + DateTime.Now.ToString("MMdd") + ".csv";

                //讀取當天同一堂課的點名檔案
                if(File.Exists(folderPath + "\\" + labclass.Text))
                {
                    string csvStr = File.ReadAllText(folderPath + "\\" + labclass.Text);
                    string[] csvArray = csvStr.Split('\n');
                    listView1.Clear();
                    for (int i = 0; i < csvArray.Length; i++)
                    {
                        var new_item = new ListViewItem();

                        foreach (string item in csvArray[i].Split(','))
                        {
                            if (i == 0)
                                listView1.Columns.Add(item, 100);
                            else
                                if (new_item.Text == "")
                                new_item.Text = item;
                            else
                                new_item.SubItems.Add(item);
                        }
                        if (i != 0)
                            listView1.Items.Add(new_item);
                    }
                }

                //新增點名開始時間欄位
                listView1.Columns.Add(DateTime.Now.ToString("HH:mm"), 100);
                for (int i = 0; i < listView1.Items.Count; i++)
                    listView1.Items[i].SubItems.Add(false.ToString());

                //清空上次出席名單
                StreamWriter sw = new StreamWriter("./list.txt");
                sw.WriteLine("");
                sw.Close();

                t_strat = new TimeSpan(DateTime.Now.Ticks);
                timer1.Enabled = true;
                var values = new Dictionary<string, string>();
                values["Do"] = "getFeature";
                values["class_id"] = class_id;
                WebPost(values);
                btn_start.Text = "停止點名";
                
                
            }
            else if(comboBox1.Text != "請選擇想查詢的課程" && btn_start.Text == "停止點名")
            {
                end_checkin();
            }
        }
        private void Form2_Load(object sender, EventArgs e)
        {
            //MessageBox.Show(sender.GetType().Name);
            if (sender.GetType().Name == "Form2")
            {
                explorer.StartInfo.FileName = ".\\checkFace_app\\checkFace_app.exe";
                explorer.Start();
                t_strat = new TimeSpan(DateTime.Now.Ticks);
                Time_checkExe.Enabled = true;
                btn_start.Enabled = false;
                btn_start.Text = "辨識啟動";
                form3.Show();
            }
            this.Visible = false;
            Form1 form1 = new Form1();//產生Form2的物件，才可以使用它所提供的Method
            
            
            form1.ShowDialog();
            this.Visible = true;
            labUser.Text = form1.TextBoxMsg;
            //labUser.Text = "108406011";

            //載入教師有的課程清單
            var values = new Dictionary<string, string>
            {
                { "_ID", labUser.Text },
                { "Do", "getClass" }
            };
            WebPost(values);
            listView1.View = View.Details;
            listView1.GridLines = true;
            listView1.LabelEdit = false;
            listView1.FullRowSelect = true;
            listView1.Scrollable = true;
            listView1.Items.Clear();
            listView1.Columns.Clear();
            //this.RightToLeft = System.Windows.Forms.RightToLeft.No;
            //listView1.Alignment=

        }

        private void button3_Click(object sender, EventArgs e)
        {
           
            explorer.StartInfo.FileName = ".\\checkFace_app\\checkFace_app.exe";
            explorer.Start();
            t_strat = new TimeSpan(DateTime.Now.Ticks);
            Time_checkExe.Enabled = true;
            btn_start.Enabled = false;

        }

        private void button4_Click(object sender, EventArgs e)
        {
            /*string execPath = AppDomain.CurrentDomain.BaseDirectory;
            MessageBox.Show(execPath);*/
            //Time_checkExe.Enabled = !Time_checkExe.Enabled;
            if(labclass.Text == "")
            {
                var result = MessageBox.Show("尚未進行點名, 無點名紀錄可匯出\n是否改匯出註冊狀況",
                                            "點名紀錄匯出提示",
                                             MessageBoxButtons.YesNo,
                                             MessageBoxIcon.Question);
                if(result == DialogResult.Yes)
                    DownloadCSV(comboBox1.Text+".csv");
            }
            else
                DownloadCSV(labclass.Text);

        }

        private void timer1_Tick(object sender, EventArgs e)
        {
            TimeSpan t_end = new TimeSpan(DateTime.Now.Ticks);
            string time = t_end.Subtract(t_strat).Minutes.ToString()+":"+t_end.Subtract(t_strat).Seconds.ToString();
            labExe.Text = "持續時間：" + time;
            try
            {
                string readText = File.ReadAllText("./list.txt");
                //label4.Text = readText;
                string[] present = readText.Split(';');
                foreach (ListViewItem item in listView1.Items)
                {
                    foreach (string number in present)
                    {
                        if (item.SubItems[1].Text == number)
                        {
                            item.SubItems[listView1.Columns.Count - 1].Text = true.ToString();
                            if (present_mail.IndexOf(number) != -1)
                            {
                                present_mail.Remove(number);
                                string ti = DateTime.Now.ToString("F");
                                var text = new BodyBuilder();
                                text.HtmlBody = $@"<h2>點名成功通知<br>
                                                <p>您已於{ti}點名成功<br>";
                                SendAutomatedEmail(number, number + "@stud.sju.edu.tw", text, "student");
                            }
                        }
                    }
                }
            }
            catch (Exception) { }

            if (t_end.Subtract(t_strat).TotalSeconds >= Convert.ToInt32(txtTime.Text)*60)
            {
                end_checkin();
            }
        }

        private void Timee_checkExe_Tick(object sender, EventArgs e)
        {
            TimeSpan t_end = new TimeSpan(DateTime.Now.Ticks);
            label7.Text = t_end.Subtract(t_strat).TotalSeconds.ToString();
            checkExe();
        }

        private void Form2_FormClosing(object sender, FormClosingEventArgs e)
        {
            try
            {                
                explorer.Close();
                Process[] processes = Process.GetProcessesByName("checkFace_app");
                for (int i = 0; i < processes.Length; i++)
                    processes[i].Kill();
                explorer.Kill();
            }
            catch { }
        }

        private void button5_Click(object sender, EventArgs e)
        {
            /*string ti = DateTime.Now.ToString("F");
            var text = new BodyBuilder();
            text.HtmlBody = $@"<h2>點名成功通知<br>
                            <p>您已於{ti}點名成功<br>";

            SendAutomatedEmail("eric", "ericqazw4107@gmail.com", text);*/
            //System.IO.Directory.CreateDirectory(@"C:\User");

            MessageBox.Show(listView1.Columns.Count.ToString());
            
        }

        private void btn_mail_Click(object sender, EventArgs e)
        {
            if (!File.Exists(labclass.Text))
                DownloadCSV(labclass.Text);
            

            var builder = new BodyBuilder();
            string[] name = labclass.Text.Split('_');
            // Set the plain-text version of the message text
            builder.HtmlBody = $@"<h2>{name[1]}課 點名結果<br>";//

            // We may also want to attach a calendar event for Monica's party...
            builder.Attachments.Add(folderPath + "\\" + labclass.Text); //

            //----------------------mail.sju.edu.tw---------------------
            if (labUser.Text == "108406011")
                SendAutomatedEmail(labUser.Text, labUser.Text + "@stud.sju.edu.tw", builder, "teacher");
            else
                SendAutomatedEmail(labUser.Text, labUser.Text + "@mail.sju.edu.tw", builder, "teacher");

        }

        private void comboBox1_SelectedIndexChanged(object sender, EventArgs e)
        {
            string classId = comboBox1.Text.Split(' ')[0];
            var values1 = new Dictionary<string, string>();
            values1["Do"] = "set_roll_call";
            values1["class_id"] = classId;
            WebPost(values1);
        }
    }
}
