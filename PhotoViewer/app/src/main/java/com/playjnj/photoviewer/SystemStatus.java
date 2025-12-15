package com.playjnj.photoviewer;

import com.google.gson.annotations.SerializedName;

/**
 * 시스템 전체 상태 모델
 * GET /api/bollard/status/ 응답과 매핑
 */
public class SystemStatus {
    @SerializedName("setting")
    private BollardSettings setting;

    @SerializedName("state")
    private BollardState state;

    public BollardSettings getSetting() {
        return setting;
    }

    public void setSetting(BollardSettings setting) {
        this.setting = setting;
    }

    public BollardState getState() {
        return state;
    }

    public void setState(BollardState state) {
        this.state = state;
    }
}
