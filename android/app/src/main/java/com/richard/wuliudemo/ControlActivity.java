package com.richard.wuliudemo;

import android.os.Bundle;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.RadioGroup;
import android.widget.Spinner;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;
import org.eclipse.paho.client.mqttv3.MqttMessage;

public class ControlActivity extends AppCompatActivity {
    private Spinner redLightSpinner;
    private Spinner redGreenSpinner;
    private Spinner rotateSpinner;
    private Button sendButton;
    private Button buttonRotate;
    private MqttClientManager mqttClientManager;
    private EditText editText;
    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.control_activity);

        // 初始化 MqttClientManager
        mqttClientManager = new MqttClientManager(this, new MqttClientManager.MqttCallbackHandler() {
            @Override
            public void onMessageReceived(String topic, MqttMessage message) {
                // 处理接收到的消息
                System.out.println("Message received: Topic: " + topic + ", Message: " + message.toString());
            }
        });

        // 初始化 Spinner 和 Button
        redLightSpinner = findViewById(R.id.spinner_redlight);
        redGreenSpinner = findViewById(R.id.spinner_redgreen);
        rotateSpinner = findViewById(R.id.spinner_rotate);
        sendButton = findViewById(R.id.buttonSend);
        buttonRotate = findViewById(R.id.button_rotate);

        // 初始化选项数组
        String[] redLightOptions = {"红绿灯1", "红绿灯2", "红绿灯3", "红绿灯4", "红绿灯5"};
        String[] redGreenOptions = {"红灯亮", "绿灯亮"};
        String[] rotateOptions = {"道闸1", "道闸2", "道闸3"};

        // 设置 Spinner 的 Adapter
        ArrayAdapter<String> redLightAdapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_item, redLightOptions);
        redLightAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        redLightSpinner.setAdapter(redLightAdapter);

        ArrayAdapter<String> redGreenAdapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_item, redGreenOptions);
        redGreenAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        redGreenSpinner.setAdapter(redGreenAdapter);

        ArrayAdapter<String> rotateAdapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_item, rotateOptions);
        rotateAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        rotateSpinner.setAdapter(rotateAdapter);

        editText = findViewById(R.id.editText);//绑定输入框

        // 设置按钮点击事件
        sendButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // 读取下拉框中的选项
                String lastOptionOfRedLight = redLightSpinner.getSelectedItem().toString();
                char lastCharOfId = lastOptionOfRedLight.charAt(lastOptionOfRedLight.length() - 1);
                String idToSend = String.valueOf(lastCharOfId);

                String redGreenStatus = redGreenSpinner.getSelectedItem().toString();
                int RedstatusToSend = redGreenStatus.equals("红灯亮") ? 0 : 1;
                String statusToSend = String.valueOf(RedstatusToSend);
                mqttClientManager.ToMessage(idToSend, statusToSend);
                //读取输入框内容
                String input = editText.getText().toString();
                if (input.isEmpty()) {
                    Toast.makeText(ControlActivity.this, "请输入数值", Toast.LENGTH_SHORT).show();
                    return;
                }
                try {
                    double num = Double.parseDouble(input);
                    int Time = (int) Math.round(num); // 四舍五入

                    if (Time < 1 || Time > 100) {
                        Toast.makeText(ControlActivity.this, "输入的数值不合规", Toast.LENGTH_SHORT).show();
                    } else {
                        String time = String.valueOf(Time);
                        // 调用MQTT客户端的Message方法
                        mqttClientManager.Message(idToSend, statusToSend, time);
                        Toast.makeText(ControlActivity.this, "数值已发送: " + time, Toast.LENGTH_SHORT).show();
                    }

                } catch (NumberFormatException e) {
                    Toast.makeText(ControlActivity.this, "请输入有效的数字", Toast.LENGTH_SHORT).show();
                }


            }
        });

        buttonRotate.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // 读取下拉框中的选项
                String lastOptionOfRotate = rotateSpinner.getSelectedItem().toString();
                char ID = lastOptionOfRotate.charAt(lastOptionOfRotate.length() - 1);
                String id = String.valueOf(ID);

                int status = 1;

                // 发送MQTT消息
                mqttClientManager.SendMessage(id, String.valueOf(status));
            }
        });
    }
}
