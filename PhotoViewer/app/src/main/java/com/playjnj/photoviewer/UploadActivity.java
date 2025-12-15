package com.playjnj.photoviewer;

import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.net.Uri;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.activity.result.ActivityResult;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;
import androidx.core.view.WindowCompat;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;

import okhttp3.MediaType;
import okhttp3.MultipartBody;
import okhttp3.RequestBody;
import okhttp3.ResponseBody;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class UploadActivity extends AppCompatActivity {
    private EditText tokenEdit;
    private EditText titleEdit;
    private EditText textEdit;
    private Button btnPickImage;
    private TextView pageTitleText;
    private Button btnSubmit;
    private Button btnDelete;
    private ImageView imagePreview;

    private Bitmap pickedBitmap;
    private int editingPostId = -1;
    private String existingImageUrl = null;

    private ActivityResultLauncher<Intent> pickImageLauncher;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_upload);

        WindowCompat.setDecorFitsSystemWindows(getWindow(), false);

        // 카메라 펀치홀, 노치, 시스템바 등에 대한 safearea 패딩 적용
        View root = findViewById(R.id.root_layout_upload);
        final int origLeft = root.getPaddingLeft();
        final int origTop = root.getPaddingTop();
        final int origRight = root.getPaddingRight();
        final int origBottom = root.getPaddingBottom();
        ViewCompat.setOnApplyWindowInsetsListener(root, (v, windowInsets) -> {
            Insets insets = windowInsets.getInsets(WindowInsetsCompat.Type.systemBars() | WindowInsetsCompat.Type.displayCutout());
            v.setPadding(origLeft + insets.left, origTop + insets.top, origRight + insets.right, origBottom + insets.bottom);
            return windowInsets;
        });
        ViewCompat.requestApplyInsets(root);

        pageTitleText = findViewById(R.id.uploadTitle);
        tokenEdit = findViewById(R.id.tokenEdit);
        titleEdit = findViewById(R.id.titleEdit);
        textEdit = findViewById(R.id.textEdit);
        btnPickImage = findViewById(R.id.btnPickImage);
        btnSubmit = findViewById(R.id.btnSubmit);
        btnDelete = findViewById(R.id.btnDelete);
        imagePreview = findViewById(R.id.imagePreview);

        Intent intent = getIntent();
        if (intent != null) {
            editingPostId = intent.getIntExtra("post_id", -1);
            String incomingTitle = intent.getStringExtra("title");
            String incomingText = intent.getStringExtra("text");
            existingImageUrl = intent.getStringExtra("image_url");
            // 게시글 수정 모드일 경우 intent 에서 받아온 데이터로 UI 데이터 바꾸기 채우기
            if (editingPostId > 0) {
                pageTitleText.setText("게시글 수정");
                if (incomingTitle != null) titleEdit.setText(incomingTitle);
                if (incomingText != null) textEdit.setText(incomingText);
                btnSubmit.setText("수정");
                btnDelete.setVisibility(View.VISIBLE);
                // 재업로드 방지
                if (existingImageUrl != null && !existingImageUrl.isEmpty()) {
                    new Thread(() -> {
                        try {
                            URL url = new URL(existingImageUrl);
                            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                            conn.setConnectTimeout(5000);
                            conn.setReadTimeout(5000);
                            InputStream is = conn.getInputStream();
                            final Bitmap bm = BitmapFactory.decodeStream(is);
                            if (is != null) try { is.close(); } catch (IOException ignored) {}
                            conn.disconnect();
                            if (bm != null) runOnUiThread(() -> imagePreview.setImageBitmap(bm));
                        } catch (IOException e) {
                            e.printStackTrace();
                        }
                    }).start();
                }

                // 삭제 버튼 기능 구현
                btnDelete.setOnClickListener(v -> {
                    String token = tokenEdit.getText().toString().trim();
                    if (token.isEmpty()) {
                        Toast.makeText(UploadActivity.this, "토큰을 입력하세요", Toast.LENGTH_SHORT).show();
                        return;
                    }
                    String authHeader = "Token " + token;
                    btnDelete.setEnabled(false);
                    ApiService api = RetrofitClient.getApiService();
                    Call<ResponseBody> delCall = api.deletePost(authHeader, editingPostId);
                    delCall.enqueue(new Callback<ResponseBody>() {
                        @Override
                        public void onResponse(Call<ResponseBody> call, Response<ResponseBody> response) {
                            btnDelete.setEnabled(true);
                            if (response.isSuccessful()) {
                                Toast.makeText(UploadActivity.this, "삭제 성공", Toast.LENGTH_SHORT).show();
                                setResult(RESULT_OK);
                                finish();
                            } else {
                                String msg = "삭제 실패: HTTP " + response.code();
                                try {
                                    if (response.errorBody() != null) msg += "\n" + response.errorBody().string();
                                } catch (IOException ignored) {}
                                Toast.makeText(UploadActivity.this, msg, Toast.LENGTH_LONG).show();
                            }
                        }

                        @Override
                        public void onFailure(Call<ResponseBody> call, Throwable t) {
                            btnDelete.setEnabled(true);
                            Toast.makeText(UploadActivity.this, "삭제 실패: " + t.getMessage(), Toast.LENGTH_LONG).show();
                        }
                    });
                });
            }
        }

        pickImageLauncher = registerForActivityResult(
                new ActivityResultContracts.StartActivityForResult(),
                (ActivityResult result) -> {
                    if (result.getResultCode() == RESULT_OK && result.getData() != null) {
                        Uri uri = result.getData().getData();
                        if (uri != null) {
                            try (InputStream is = getContentResolver().openInputStream(uri)) {
                                Bitmap bm = BitmapFactory.decodeStream(is);
                                pickedBitmap = bm;
                                imagePreview.setImageBitmap(bm);
                            } catch (IOException e) {
                                e.printStackTrace();
                                Toast.makeText(this, "이미지 로드 실패", Toast.LENGTH_SHORT).show();
                            }
                        }
                    }
                }
        );

        btnPickImage.setOnClickListener(v -> {
            Intent pick = new Intent(Intent.ACTION_GET_CONTENT);
            pick.setType("image/*");
            pick.addCategory(Intent.CATEGORY_OPENABLE);
            pickImageLauncher.launch(Intent.createChooser(pick, "이미지 선택"));
        });
    }

    public void onClickSubmit(View v) {
        String token = tokenEdit.getText().toString().trim();
        if (token.isEmpty()) {
            Toast.makeText(this, "토큰을 입력하세요", Toast.LENGTH_SHORT).show();
            return;
        }
        String authHeader = token.startsWith("Token ") || token.startsWith("Bearer ") ? token : ("Token " + token);
        submitPost(authHeader);
    }

    private void submitPost(String authHeader) {
        String title = titleEdit.getText().toString().trim();
        String text = textEdit.getText().toString().trim();

        if (title.isEmpty()) {
            Toast.makeText(this, "제목을 입력하세요", Toast.LENGTH_SHORT).show();
            return;
        }

        btnSubmit.setEnabled(false);

        RequestBody titlePart = RequestBody.create(title, MediaType.parse("text/plain; charset=utf-8"));
        RequestBody textPart = RequestBody.create(text, MediaType.parse("text/plain; charset=utf-8"));

        MultipartBody.Part imagePart = null;
        if (pickedBitmap != null) {
            ByteArrayOutputStream baos = new ByteArrayOutputStream();
            pickedBitmap.compress(Bitmap.CompressFormat.JPEG, 85, baos);
            byte[] bytes = baos.toByteArray();
            RequestBody req = RequestBody.create(bytes, MediaType.parse("image/jpeg"));
            imagePart = MultipartBody.Part.createFormData("image", "upload.jpg", req);
        }

        ApiService api = RetrofitClient.getApiService();
        Call<ResponseBody> call;

        // 게시글 수정 or 새 게시글 업로드
        if (editingPostId > 0) {
            call = api.updatePost(authHeader, editingPostId, titlePart, textPart, imagePart);
        } else {
            call = api.createPost(authHeader, titlePart, textPart, imagePart);
        }

        call.enqueue(new Callback<ResponseBody>() {
            @Override
            public void onResponse(Call<ResponseBody> call, Response<ResponseBody> response) {
                btnSubmit.setEnabled(true);
                if (response.isSuccessful()) {
                    Toast.makeText(UploadActivity.this, editingPostId > 0 ? "수정 성공" : "업로드 성공", Toast.LENGTH_SHORT).show();
                    setResult(RESULT_OK);
                    finish();
                } else {
                    String msg = (editingPostId > 0 ? "수정 실패: HTTP " : "업로드 실패: HTTP ") + response.code();
                    try {
                        if (response.errorBody() != null) msg += "\n" + response.errorBody().string();
                    } catch (IOException ignored) {}
                    Toast.makeText(UploadActivity.this, msg, Toast.LENGTH_LONG).show();
                }
            }

            @Override
            public void onFailure(Call<ResponseBody> call, Throwable t) {
                btnSubmit.setEnabled(true);
                Toast.makeText(UploadActivity.this, (editingPostId > 0 ? "수정 실패: " : "업로드 실패: ") + t.getMessage(), Toast.LENGTH_LONG).show();
            }
        });
    }
}
