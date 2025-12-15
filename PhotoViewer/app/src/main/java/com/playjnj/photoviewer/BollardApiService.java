package com.playjnj.photoviewer;

import okhttp3.ResponseBody;
import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.GET;
import retrofit2.http.Header;
import retrofit2.http.PATCH;
import retrofit2.http.POST;

import java.util.Map;

/**
 * 볼라드 시스템 REST API 인터페이스
 * Django /api/bollard/ 엔드포인트와 통신
 */
public interface BollardApiService {

    /**
     * 볼라드 제어
     * POST /api/bollard/control/
     * 
     * @param auth  인증 토큰 (예: "Token abc123")
     * @param body  {"action": "open" | "close" | "auto" | "start_system" | "stop_system"}
     */
    @POST("bollard/control/")
    Call<ResponseBody> controlBollard(
            @Header("Authorization") String auth,
            @Body Map<String, String> body
    );

    /**
     * 시스템 전체 상태 조회
     * GET /api/bollard/status/
     * 
     * @param auth 인증 토큰
     * @return SystemStatus (setting + state)
     */
    @GET("bollard/status/")
    Call<SystemStatus> getSystemStatus(
            @Header("Authorization") String auth
    );

    /**
     * 현재 볼라드 상태 조회
     * GET /api/bollard/state/
     * 
     * @param auth 인증 토큰
     * @return BollardState (is_closed, counter, manual_mode)
     */
    @GET("bollard/state/")
    Call<BollardState> getBollardState(
            @Header("Authorization") String auth
    );

    /**
     * 활성 설정 조회
     * GET /api/bollard/settings/active/
     * 
     * @param auth 인증 토큰
     * @return BollardSettings
     */
    @GET("bollard/settings/active/")
    Call<BollardSettings> getActiveSettings(
            @Header("Authorization") String auth
    );

    /**
     * 활성 설정 업데이트
     * PATCH /api/bollard/settings/update_active/
     * 
     * @param auth 인증 토큰
     * @param body {"occupy_ratio": 30, "maintain_frame": 10, ...}
     */
    @PATCH("bollard/settings/update_active/")
    Call<ResponseBody> updateSettings(
            @Header("Authorization") String auth,
            @Body Map<String, Object> body
    );
}
