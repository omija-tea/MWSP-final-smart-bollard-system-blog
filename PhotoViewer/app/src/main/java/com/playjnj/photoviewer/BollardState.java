package com.playjnj.photoviewer;

import com.google.gson.annotations.SerializedName;

/**
 * 볼라드 현재 상태 모델
 * GET /api/bollard/state/ 응답과 매핑
 */
public class BollardState {
    @SerializedName("is_closed")
    private boolean isClosed;

    @SerializedName("counter")
    private int counter;

    @SerializedName("manual_mode")
    private boolean manualMode;

    public boolean isClosed() {
        return isClosed;
    }

    public void setClosed(boolean closed) {
        isClosed = closed;
    }

    public int getCounter() {
        return counter;
    }

    public void setCounter(int counter) {
        this.counter = counter;
    }

    public boolean isManualMode() {
        return manualMode;
    }

    public void setManualMode(boolean manualMode) {
        this.manualMode = manualMode;
    }

    /**
     * 상태를 한글로 반환
     */
    public String getStatusDisplay() {
        return isClosed ? "닫힘" : "열림";
    }

    /**
     * 모드를 한글로 반환
     */
    public String getModeDisplay() {
        return manualMode ? "수동 모드" : "자동 모드";
    }
}
