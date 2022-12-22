using System;
using System.Collections.Generic;
using System.Windows.Forms;
using System.Net.Http;
using Newtonsoft.Json.Linq;

namespace TeacherApp
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
        }

        public string TextBoxMsg
        {
            get
            {
                return textBox1.Text;
            }
        }
        
         
        private async void button1_Click(object sender, EventArgs e)
        {
            
            HttpClient client = new HttpClient();
            var values = new Dictionary<string, string>
            {
                { "_ID", textBox1.Text },
                { "password", textBox2.Text }
            };

            string url = Class_constant.Url+"/api/login";
            var data = new FormUrlEncodedContent(values);
            var response = await client.PostAsync(url, data);
            string result = response.Content.ReadAsStringAsync().Result;
            
            JObject json = JObject.Parse(result);
            string msg = json.Value<String>("msg");

            if (msg == "OK")
            {
                //關閉登入視窗
                this.DialogResult = DialogResult.OK;
                this.Close();
            }
            label3.Text = json.Value<String>("msg");
        }

        private void Form1_FormClosing(object sender, FormClosingEventArgs e)
        {
            if (this.DialogResult != DialogResult.OK)
                Application.Exit();
        }
    }
}
