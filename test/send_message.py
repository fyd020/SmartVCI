import logging
import requests
import sys


logger = logging.getLogger(__name__)


class SendMessage:
    
    def time_parser(self, duration: int) -> None:
        try:
            millis = int(duration)
        except ValueError:
            logger.error(f"time_duration must be integer type")
        else:
            seconds=(millis/1000)%60
            seconds = int(seconds)
            minutes=(millis/(1000*60))%60
            minutes = int(minutes)
            hours=(millis/(1000*60*60))%24
            logger.info("%d:%d:%d" % (hours, minutes, seconds))
            return str("%d时%d分%d秒" % (hours, minutes, seconds))
        
    def send_message(self, 
                          BUILD_STATUS: str, 
                          ProjectName: str, 
                          BUILD_URL: str, 
                          BUILD_NUMBER: str, 
                          duration: int) -> None:
    
        headers = {"Content-Type": "text/plain"}
        send_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=e3384ed9-20c5-440f-8392-5e0aadfc81e4"
        report = f"{BUILD_URL}/allure/" 
        result = ""
        colour = ""
        if BUILD_STATUS == "SUCCESS":
            result = "成功"
            colour = "info"
        elif BUILD_STATUS == "FAILURE":
            result = "失败"
            colour = "warning"
        elif BUILD_STATUS=="UNSTABLE":
            result = "中断"
            colour = "comment"
        send_data = {
            "msgtype" : "markdown", 
            "markdown" : {
                "content" : f"**<font color=\"{colour}\">【{ProjectName}】</font>构建"+f"<font color=\"{colour}\">{result}</font>**！！！\r\n" +  
                        f"> 项目名称：<font color=\"{colour}\"> {ProjectName} </font> \n" +  
                        f"> 构建编号：<font color=\"{colour}\"> # {BUILD_NUMBER} </font> \n" +  
                        f"> 构建用时：<font color=\"{colour}\"> {self.time_parser(duration)} </font> \n" +  
                        f"[报告链接]({report})\n"+
                        f"[控制台]({BUILD_URL})"
            }
        }
        res = requests.post(url=send_url, headers=headers, json=send_data)
        logger.info(res.text)


if __name__ == "__main__":
    BUILD_STATUS = sys.argv[1] 
    ProjectName = sys.argv[2] 
    BUILD_URL = sys.argv[3] 
    BUILD_NUMBER = sys.argv[4] 
    duration = sys.argv[5] 
    noti_obj = SendMessage()
    noti_obj.send_message(BUILD_STATUS, ProjectName, BUILD_URL, BUILD_NUMBER, duration)
