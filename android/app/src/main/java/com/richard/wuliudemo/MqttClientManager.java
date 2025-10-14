package com.richard.wuliudemo;

import android.content.Context;

import org.eclipse.paho.android.service.MqttAndroidClient;
import org.eclipse.paho.client.mqttv3.IMqttActionListener;
import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
import org.eclipse.paho.client.mqttv3.IMqttToken;
import org.eclipse.paho.client.mqttv3.MqttCallback;
import org.eclipse.paho.client.mqttv3.MqttConnectOptions;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;

public class MqttClientManager {
    private MqttAndroidClient mqttClient;
    private Context context;
    private MqttCallbackHandler callbackHandler;

    public MqttClientManager(Context context, MqttCallbackHandler callbackHandler) {
        this.context = context;
        this.callbackHandler = callbackHandler;
        String serverUri = "tcp://192.168.124.10:1883";
        String clientId = "AndroidDevice_" + System.currentTimeMillis();
        mqttClient = new MqttAndroidClient(context, serverUri, clientId);
        mqttClient.setCallback(new MqttCallback() {
            @Override
            public void connectionLost(Throwable cause) {
                System.out.println("Connection lost!");
                cause.printStackTrace();
            }

            @Override
            public void messageArrived(String topic, MqttMessage message) throws Exception {
                System.out.println("Message arrived. Topic: " + topic + " Message: " + message.toString());
                if (callbackHandler != null) {
                    callbackHandler.onMessageReceived(topic, message);
                }
            }

            @Override
            public void deliveryComplete(IMqttDeliveryToken token) {
                System.out.println("Delivery complete!");
            }
        });

        MqttConnectOptions options = new MqttConnectOptions();
        options.setCleanSession(true);
        options.setAutomaticReconnect(true);

        try {
            mqttClient.connect(options, null, new IMqttActionListener() {
                @Override
                public void onSuccess(IMqttToken asyncActionToken) {
                    System.out.println("Connected");
                    subscribeToTopics(new String[]{"network/temp_info", "express/truck_info/#", "express/dest_where/#"});
                }

                @Override
                public void onFailure(IMqttToken asyncActionToken, Throwable exception) {
                    System.out.println("Failed to connect to: " + serverUri);
                    exception.printStackTrace();
                }
            });
        } catch (MqttException e) {
            e.printStackTrace();
            System.out.println("连接失败!");
        }
    }

    private void subscribeToTopics(String[] topics) {
        try {
            for (String topic : topics) {
                mqttClient.subscribe(topic, 1);
                System.out.println("Subscribed to topic: " + topic);
            }
        } catch (MqttException e) {
            e.printStackTrace();
            System.out.println("Failed to subscribe to topics.");
        }
    }

    public void publishMessage(String id, String packageId, String dest) {
        String payload = id + "_" + packageId + "_" + dest;
        try {
            mqttClient.publish("app/task_set/id_package_dest", new MqttMessage(payload.getBytes()));
        } catch (MqttException e) {
            e.printStackTrace();
        }
    }
    //****发送指令****
    public void Message(String idToSend, String statusToSend,String time) {
        String payload = idToSend + "_" + statusToSend +"_" + time;
        try {
            MqttConnectOptions options = new MqttConnectOptions();
            mqttClient.publish("network/traffic_set",new MqttMessage(payload.getBytes()));
        } catch (MqttException e) {
            e.printStackTrace();
        }
    }
    public void ToMessage(String idToSend, String statusToSend) {
        String payload = idToSend + "_" + statusToSend;
        try {
            MqttConnectOptions options = new MqttConnectOptions();
            mqttClient.publish("network/traffic_set_color",new MqttMessage(payload.getBytes()));
        } catch (MqttException e) {
            e.printStackTrace();
        }
    }
    public void SendMessage(String id, String status) {
        String payload = id + "_" + status;
        try {
            MqttConnectOptions options = new MqttConnectOptions();
            mqttClient.publish("network/git_set",new MqttMessage(payload.getBytes()));
        } catch (MqttException e) {
            e.printStackTrace();
        }
    }
    //*******
    public interface MqttCallbackHandler {
        void onMessageReceived(String topic, MqttMessage message);
    }
}
