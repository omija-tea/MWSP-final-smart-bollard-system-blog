package com.playjnj.photoviewer;

import com.google.gson.annotations.SerializedName;


public class BollardSettings {
    @SerializedName("id")
    private int id;

    @SerializedName("occupy_ratio")
    private int occupyRatio;

    @SerializedName("maintain_frame")
    private int maintainFrame;

    @SerializedName("target_object")
    private String targetObject;

    @SerializedName("is_active")
    private boolean isActive;

    @SerializedName("raspberry_pi_host")
    private String raspberryPiHost;

    @SerializedName("raspberry_pi_port")
    private int raspberryPiPort;

    @SerializedName("grpc_server_port")
    private int grpcServerPort;

    // Getters and Setters
    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public int getOccupyRatio() {
        return occupyRatio;
    }

    public void setOccupyRatio(int occupyRatio) {
        this.occupyRatio = occupyRatio;
    }

    public int getMaintainFrame() {
        return maintainFrame;
    }

    public void setMaintainFrame(int maintainFrame) {
        this.maintainFrame = maintainFrame;
    }

    public String getTargetObject() {
        return targetObject;
    }

    public void setTargetObject(String targetObject) {
        this.targetObject = targetObject;
    }

    public boolean isActive() {
        return isActive;
    }

    public void setActive(boolean active) {
        isActive = active;
    }

    public String getRaspberryPiHost() {
        return raspberryPiHost;
    }

    public void setRaspberryPiHost(String raspberryPiHost) {
        this.raspberryPiHost = raspberryPiHost;
    }

    public int getRaspberryPiPort() {
        return raspberryPiPort;
    }

    public void setRaspberryPiPort(int raspberryPiPort) {
        this.raspberryPiPort = raspberryPiPort;
    }

    public int getGrpcServerPort() {
        return grpcServerPort;
    }

    public void setGrpcServerPort(int grpcServerPort) {
        this.grpcServerPort = grpcServerPort;
    }


    public String getSystemStatusDisplay() {
        return isActive ? "실행 중" : "정지됨";
    }
}
