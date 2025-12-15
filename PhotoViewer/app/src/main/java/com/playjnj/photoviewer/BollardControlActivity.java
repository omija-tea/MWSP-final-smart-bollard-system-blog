package com.playjnj.photoviewer;

import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowCompat;
import androidx.core.view.WindowInsetsCompat;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

import okhttp3.OkHttpClient;
import okhttp3.ResponseBody;
import okhttp3.logging.HttpLoggingInterceptor;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

/**
 * 볼라드 제어 Activity
 * 볼라드 열기/닫기/자동, 시스템 시작/정지, 설정 변경 기능 제공
 */
public class BollardControlActivity extends AppCompatActivity {

    // UI 요소
    private EditText tokenEdit;
    private TextView txtBollardStatus, txtControlMode, txtSystemStatus, txtCounter;
    private EditText editOccupyRatio, editMaintainFrame, editTargetObject;
    private Button btnRefreshStatus, btnOpen, btnClose, btnAuto;
    private Button btnStartSystem, btnStopSystem, btnSaveSettings;

    // API 클라이언트
    private BollardApiService bollardApi;

    // 상태 폴링용 핸들러 (1초마다 상태 업데이트)
    private Handler statusHandler;
    private Runnable statusRunnable;
    private boolean isPolling = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_bollard_control);
        // ActionBar가 있으므로 edge-to-edge 비활성화
        WindowCompat.setDecorFitsSystemWindows(getWindow(), true);

        // ActionBar 설정
        if (getSupportActionBar() != null) {
            getSupportActionBar().setTitle("볼라드 제어");
            getSupportActionBar().setDisplayHomeAsUpEnabled(true);
        }

        // UI 요소 바인딩
        initViews();

        // API 클라이언트 초기화
        initApiClient();

        // 버튼 클릭 리스너 설정
        setupClickListeners();

        // 상태 폴링 설정
        setupStatusPolling();
    }

    private void initViews() {
        tokenEdit = findViewById(R.id.tokenEdit);
        txtBollardStatus = findViewById(R.id.txtBollardStatus);
        txtControlMode = findViewById(R.id.txtControlMode);
        txtSystemStatus = findViewById(R.id.txtSystemStatus);
        txtCounter = findViewById(R.id.txtCounter);

        editOccupyRatio = findViewById(R.id.editOccupyRatio);
        editMaintainFrame = findViewById(R.id.editMaintainFrame);
        editTargetObject = findViewById(R.id.editTargetObject);

        btnRefreshStatus = findViewById(R.id.btnRefreshStatus);
        btnOpen = findViewById(R.id.btnOpen);
        btnClose = findViewById(R.id.btnClose);
        btnAuto = findViewById(R.id.btnAuto);
        btnStartSystem = findViewById(R.id.btnStartSystem);
        btnStopSystem = findViewById(R.id.btnStopSystem);
        btnSaveSettings = findViewById(R.id.btnSaveSettings);
    }

    private void initApiClient() {
        HttpLoggingInterceptor logging = new HttpLoggingInterceptor();
        logging.setLevel(HttpLoggingInterceptor.Level.BODY);

        OkHttpClient client = new OkHttpClient.Builder()
                .addInterceptor(logging)
                .build();

        // 볼라드 API는 /api/ 경로 사용
        String baseUrl = BuildConfig.BASE_URL + "/api/";

        Retrofit retrofit = new Retrofit.Builder()
                .baseUrl(baseUrl)
                .client(client)
                .addConverterFactory(GsonConverterFactory.create())
                .build();

        bollardApi = retrofit.create(BollardApiService.class);
    }

    private void setupClickListeners() {
        // 상태 새로고침
        btnRefreshStatus.setOnClickListener(v -> fetchSystemStatus());

        // 볼라드 제어 버튼
        btnOpen.setOnClickListener(v -> showConfirmDialog("볼라드 열기", "볼라드를 열겠습니까?", "open"));
        btnClose.setOnClickListener(v -> showConfirmDialog("볼라드 닫기", "볼라드를 닫겠습니까?", "close"));
        btnAuto.setOnClickListener(v -> sendControlCommand("auto"));

        // 시스템 제어 버튼
        btnStartSystem.setOnClickListener(v -> sendControlCommand("start_system"));
        btnStopSystem.setOnClickListener(v -> showConfirmDialog("시스템 정지", "시스템을 정지하시겠습니까?", "stop_system"));

        // 설정 저장
        btnSaveSettings.setOnClickListener(v -> saveSettings());
    }

    private void setupStatusPolling() {
        statusHandler = new Handler(Looper.getMainLooper());
        statusRunnable = new Runnable() {
            @Override
            public void run() {
                if (isPolling && hasValidToken()) {
                    fetchBollardState();
                    statusHandler.postDelayed(this, 2000); // 2초마다 폴링
                }
            }
        };
    }

    @Override
    protected void onResume() {
        super.onResume();
        // 화면 진입 시 상태 조회 및 폴링 시작
        if (hasValidToken()) {
            fetchSystemStatus();
            startPolling();
        }
    }

    @Override
    protected void onPause() {
        super.onPause();
        stopPolling();
    }

    private void startPolling() {
        if (!isPolling) {
            isPolling = true;
            statusHandler.postDelayed(statusRunnable, 2000);
        }
    }

    private void stopPolling() {
        isPolling = false;
        statusHandler.removeCallbacks(statusRunnable);
    }

    private boolean hasValidToken() {
        String token = tokenEdit.getText().toString().trim();
        return !token.isEmpty();
    }

    private String getAuthHeader() {
        String token = tokenEdit.getText().toString().trim();
        if (token.isEmpty()) {
            Toast.makeText(this, "토큰을 입력하세요", Toast.LENGTH_SHORT).show();
            return null;
        }
        // Token prefix 자동 추가
        if (!token.startsWith("Token ") && !token.startsWith("Bearer ")) {
            token = "Token " + token;
        }
        return token;
    }

    /**
     * 시스템 전체 상태 조회 (설정 + 상태)
     */
    private void fetchSystemStatus() {
        String auth = getAuthHeader();
        if (auth == null) return;

        bollardApi.getSystemStatus(auth).enqueue(new Callback<SystemStatus>() {
            @Override
            public void onResponse(Call<SystemStatus> call, Response<SystemStatus> response) {
                if (response.isSuccessful() && response.body() != null) {
                    updateUI(response.body());
                    startPolling(); // 첫 성공 후 폴링 시작
                } else {
                    handleError(response);
                }
            }

            @Override
            public void onFailure(Call<SystemStatus> call, Throwable t) {
                Toast.makeText(BollardControlActivity.this,
                        "연결 실패: " + t.getMessage(), Toast.LENGTH_LONG).show();
            }
        });
    }

    /**
     * 볼라드 상태만 조회 (폴링용)
     */
    private void fetchBollardState() {
        String auth = getAuthHeader();
        if (auth == null) return;

        bollardApi.getBollardState(auth).enqueue(new Callback<BollardState>() {
            @Override
            public void onResponse(Call<BollardState> call, Response<BollardState> response) {
                if (response.isSuccessful() && response.body() != null) {
                    updateStateUI(response.body());
                }
                // 폴링 중 오류는 무시 (다음 폴링에서 재시도)
            }

            @Override
            public void onFailure(Call<BollardState> call, Throwable t) {
                // 폴링 중 실패는 조용히 무시
            }
        });
    }

    /**
     * 전체 UI 업데이트
     */
    private void updateUI(SystemStatus status) {
        if (status.getState() != null) {
            updateStateUI(status.getState());
        }
        if (status.getSetting() != null) {
            updateSettingsUI(status.getSetting());
        }
    }

    /**
     * 상태 UI 업데이트
     */
    private void updateStateUI(BollardState state) {
        // 볼라드 상태 (색상으로 구분)
        txtBollardStatus.setText(state.getStatusDisplay());
        txtBollardStatus.setTextColor(getResources().getColor(
                state.isClosed() ? android.R.color.holo_red_dark : android.R.color.holo_green_dark,
                getTheme()
        ));

        // 제어 모드
        txtControlMode.setText(state.getModeDisplay());

        // 프레임 카운터
        txtCounter.setText(String.valueOf(state.getCounter()));
    }

    /**
     * 설정 UI 업데이트
     */
    private void updateSettingsUI(BollardSettings settings) {
        // 시스템 상태
        txtSystemStatus.setText(settings.getSystemStatusDisplay());
        txtSystemStatus.setTextColor(getResources().getColor(
                settings.isActive() ? android.R.color.holo_green_dark : android.R.color.holo_red_dark,
                getTheme()
        ));

        // 설정 값 (빈 경우에만 채움 - 사용자 입력 보존)
        if (editOccupyRatio.getText().toString().isEmpty()) {
            editOccupyRatio.setText(String.valueOf(settings.getOccupyRatio()));
        }
        if (editMaintainFrame.getText().toString().isEmpty()) {
            editMaintainFrame.setText(String.valueOf(settings.getMaintainFrame()));
        }
        if (editTargetObject.getText().toString().isEmpty() ||
                editTargetObject.getText().toString().equals("motorcycle")) {
            editTargetObject.setText(settings.getTargetObject());
        }
    }

    /**
     * 확인 다이얼로그 표시
     */
    private void showConfirmDialog(String title, String message, String action) {
        new AlertDialog.Builder(this)
                .setTitle(title)
                .setMessage(message)
                .setPositiveButton("확인", (dialog, which) -> sendControlCommand(action))
                .setNegativeButton("취소", null)
                .show();
    }

    /**
     * 볼라드/시스템 제어 명령 전송
     */
    private void sendControlCommand(String action) {
        String auth = getAuthHeader();
        if (auth == null) return;

        Map<String, String> body = new HashMap<>();
        body.put("action", action);

        setControlButtonsEnabled(false);

        bollardApi.controlBollard(auth, body).enqueue(new Callback<ResponseBody>() {
            @Override
            public void onResponse(Call<ResponseBody> call, Response<ResponseBody> response) {
                setControlButtonsEnabled(true);
                if (response.isSuccessful()) {
                    String msg = getActionMessage(action);
                    Toast.makeText(BollardControlActivity.this, msg, Toast.LENGTH_SHORT).show();
                    // 상태 즉시 새로고침
                    fetchSystemStatus();
                } else {
                    handleError(response);
                }
            }

            @Override
            public void onFailure(Call<ResponseBody> call, Throwable t) {
                setControlButtonsEnabled(true);
                Toast.makeText(BollardControlActivity.this,
                        "명령 실패: " + t.getMessage(), Toast.LENGTH_LONG).show();
            }
        });
    }

    /**
     * 설정 저장
     */
    private void saveSettings() {
        String auth = getAuthHeader();
        if (auth == null) return;

        // 입력값 검증
        String occupyRatioStr = editOccupyRatio.getText().toString().trim();
        String maintainFrameStr = editMaintainFrame.getText().toString().trim();
        String targetObject = editTargetObject.getText().toString().trim();

        if (occupyRatioStr.isEmpty() || maintainFrameStr.isEmpty()) {
            Toast.makeText(this, "점유율과 유지 프레임을 입력하세요", Toast.LENGTH_SHORT).show();
            return;
        }

        int occupyRatio, maintainFrame;
        try {
            occupyRatio = Integer.parseInt(occupyRatioStr);
            maintainFrame = Integer.parseInt(maintainFrameStr);
        } catch (NumberFormatException e) {
            Toast.makeText(this, "숫자를 올바르게 입력하세요", Toast.LENGTH_SHORT).show();
            return;
        }

        // 범위 검증
        if (occupyRatio < 1 || occupyRatio > 100) {
            Toast.makeText(this, "점유율은 1-100 사이의 값이어야 합니다", Toast.LENGTH_SHORT).show();
            return;
        }
        if (maintainFrame < 1) {
            Toast.makeText(this, "유지 프레임은 1 이상이어야 합니다", Toast.LENGTH_SHORT).show();
            return;
        }

        Map<String, Object> body = new HashMap<>();
        body.put("occupy_ratio", occupyRatio);
        body.put("maintain_frame", maintainFrame);
        if (!targetObject.isEmpty()) {
            body.put("target_object", targetObject);
        }

        btnSaveSettings.setEnabled(false);

        bollardApi.updateSettings(auth, body).enqueue(new Callback<ResponseBody>() {
            @Override
            public void onResponse(Call<ResponseBody> call, Response<ResponseBody> response) {
                btnSaveSettings.setEnabled(true);
                if (response.isSuccessful()) {
                    Toast.makeText(BollardControlActivity.this,
                            "설정이 저장되었습니다", Toast.LENGTH_SHORT).show();
                    fetchSystemStatus();
                } else {
                    handleError(response);
                }
            }

            @Override
            public void onFailure(Call<ResponseBody> call, Throwable t) {
                btnSaveSettings.setEnabled(true);
                Toast.makeText(BollardControlActivity.this,
                        "설정 저장 실패: " + t.getMessage(), Toast.LENGTH_LONG).show();
            }
        });
    }

    /**
     * 제어 버튼 활성화/비활성화
     */
    private void setControlButtonsEnabled(boolean enabled) {
        btnOpen.setEnabled(enabled);
        btnClose.setEnabled(enabled);
        btnAuto.setEnabled(enabled);
        btnStartSystem.setEnabled(enabled);
        btnStopSystem.setEnabled(enabled);
    }

    /**
     * 액션에 따른 메시지 반환
     */
    private String getActionMessage(String action) {
        switch (action) {
            case "open": return "볼라드가 열렸습니다";
            case "close": return "볼라드가 닫혔습니다";
            case "auto": return "자동 모드로 전환되었습니다";
            case "start_system": return "시스템이 시작되었습니다";
            case "stop_system": return "시스템이 정지되었습니다";
            default: return "명령이 전송되었습니다";
        }
    }

    /**
     * API 에러 처리
     */
    private void handleError(Response<?> response) {
        String errorMsg = "오류 발생";
        try {
            if (response.errorBody() != null) {
                errorMsg = response.errorBody().string();
            }
        } catch (IOException e) {
            errorMsg = "HTTP " + response.code();
        }
        Toast.makeText(this, errorMsg, Toast.LENGTH_LONG).show();
    }

    @Override
    public boolean onSupportNavigateUp() {
        finish();
        return true;
    }
}
