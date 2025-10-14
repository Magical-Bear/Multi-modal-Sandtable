package com.richard.wuliudemo;

import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.Spinner;
import android.widget.TextView;
import android.view.View;
import android.widget.AdapterView;
import androidx.appcompat.app.AppCompatActivity;
import org.eclipse.paho.client.mqttv3.MqttMessage;

public class MainActivity extends AppCompatActivity {

    private TextView textViewCarLocation;
    private TextView textViewCarStatus;
    private TextView textViewDriveStatus;
    private Handler handler;
    private Spinner spinnerDestinations;
    private String selectedDestination = "00"; // 默认值
    private MqttClientManager mqttClientManager;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        Button controlButton = findViewById(R.id.control);

        // 设置点击事件监听器
        controlButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // 跳转到ControlActivity
                Intent intent = new Intent(MainActivity.this, ControlActivity.class);
                startActivity(intent);
            }
        });

        // 绑定文本框
        textViewCarLocation = findViewById(R.id.textViewCar01);
        textViewCarStatus = findViewById(R.id.textViewCar02);
        textViewDriveStatus = findViewById(R.id.textViewTaskStatus);

        // 初始化 Handler
        handler = new Handler(Looper.getMainLooper());

        // 初始化 MqttClientManager
        mqttClientManager = new MqttClientManager(this, new MqttCallbackHandler());

        // 初始化Spinner
        spinnerDestinations = findViewById(R.id.spinnerDestinations);
        ArrayAdapter<CharSequence> adapter = ArrayAdapter.createFromResource(this,
                R.array.destinations_array, android.R.layout.simple_spinner_item);
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinnerDestinations.setAdapter(adapter);

        spinnerDestinations.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> parentView, View selectedItemView, int position, long id) {
                String selectedItem = (String) parentView.getItemAtPosition(position);
                selectedDestination = selectedItem.substring(selectedItem.length() - 2); // 提取编号
            }

            @Override
            public void onNothingSelected(AdapterView<?> parentView) {
                // Do nothing
            }
        });

        // 设置按钮点击事件
        Button buttonSendDestination = findViewById(R.id.buttonSendDestination);
        buttonSendDestination.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                mqttClientManager.publishMessage("1", "1", selectedDestination);  // 物流车编号和快件编号暂时固定为1
            }
        });
    }

    class MqttCallbackHandler implements MqttClientManager.MqttCallbackHandler {
        @Override
        public void onMessageReceived(String topic, MqttMessage message) {
            handler.post(() -> {
                String payload = new String(message.getPayload());
                if (topic.startsWith("express/truck_info")) {
                    String[] parts = payload.split("_");
                    String id = parts[0];
                    String state = parts[1];
                    String runningTime = parts[2];

                    String stateText;
                    String driveText;

                    switch (state) {
                        case "0":
                            stateText = "空闲";
                            driveText = "已停止";
                            runningTime = "-1";
                            break;
                        case "1":
                            stateText = "运送中";
                            driveText = "行驶中";
                            break;
                        case "2":
                            stateText = "已送达";
                            driveText = "已停止";
                            runningTime = "-1";
                            break;
                        case "3":
                            stateText = "回库";
                            driveText = "已停止";
                            runningTime = "-1";
                            break;
                        default:
                            stateText = "未知状态";
                            driveText = "未知";
                            runningTime = "-1";
                            break;
                    }

                    textViewCarStatus.setText("任务状态: " + stateText + "\n运行时间: " + runningTime + "秒");
                    textViewDriveStatus.setText("行驶状态: " + driveText);
                } else if (topic.startsWith("express/dest_where")) {
                    String[] parts = payload.split("_");
                    String id = parts[0];
                    String where = parts[1];

                    String locationText = "编号为" + id + "的小车，处于" + where + "位置";
                    textViewCarLocation.setText(locationText);
                } else {
                    textViewCarLocation.setText("小车当前在" + payload);
                }
                System.out.println("UI 更新触发 New text in textView: " + payload);
            });
        }
    }
}
