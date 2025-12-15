package com.playjnj.photoviewer;

import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.AsyncTask;
import android.os.Bundle;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;
import androidx.core.view.WindowCompat;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;

public class MainActivity extends AppCompatActivity {
    private static final int MY_PERMISSIONS_REQUEST_WRITE_EXTERNAL_STORAGE = 1;
    ImageView imgView;
    TextView textView;
    String site_url = BuildConfig.BASE_URL;
    JSONObject post_json;
    String imageUrl = null;
    Bitmap bmImg = null;
    CloadImage taskDownload;
    SwipeRefreshLayout swipeRefresh;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        WindowCompat.setDecorFitsSystemWindows(getWindow(), false);

        // 카메라 펀치홀, 노치, 시스템바 등에 대한 safearea 패딩 적용
        View root = findViewById(R.id.root_layout);
        ViewCompat.setOnApplyWindowInsetsListener(root, (v, windowInsets) -> {
            Insets insets = windowInsets.getInsets(WindowInsetsCompat.Type.systemBars() | WindowInsetsCompat.Type.displayCutout());
            v.setPadding(insets.left, insets.top, insets.right, insets.bottom);
            return windowInsets;
        });
        ViewCompat.requestApplyInsets(root);

        textView = (TextView) findViewById(R.id.textView);

        // swipe to refresh 기능 설정
        swipeRefresh = findViewById(R.id.swipeRefresh);
        if (swipeRefresh != null) {
            swipeRefresh.setOnRefreshListener(() -> {
                // Trigger the same download behavior as the button
                onClickDownload(null);
            });
        }

        // 렌더링 될때 자동으로 게시글 다운로드 시작
        root.post(() -> onClickDownload(null));

        // 볼라드 제어 버튼 클릭 리스너
        findViewById(R.id.btn_bollard).setOnClickListener(v -> {
            Intent intent = new Intent(MainActivity.this, BollardControlActivity.class);
            startActivity(intent);
        });
    }

    @Override
    protected void onResume() {
        // 새로운 게시물 게시, 게시물 수정 후 돌아올때 자동으로 다운로드
        super.onResume();
        onClickDownload(null);
    }

    public void onClickDownload(View v) {
        if (taskDownload != null && taskDownload.getStatus() == AsyncTask.Status.RUNNING) {
            taskDownload.cancel(true);
        }
        if (swipeRefresh != null && !swipeRefresh.isRefreshing()) swipeRefresh.setRefreshing(true);

        taskDownload = new CloadImage();
        taskDownload.execute(site_url + "/api_root/Post/");
        Toast.makeText(getApplicationContext(), "Download", Toast.LENGTH_LONG).show();
    }

    public void onClickUpload(View v) {
        // UploadActivity로 이동
        Intent intent = new Intent(MainActivity.this, UploadActivity.class);
        startActivity(intent);
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.main_menu, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        if (item.getItemId() == R.id.menu_bollard) {
            // 볼라드 제어 화면으로 이동
            Intent intent = new Intent(MainActivity.this, BollardControlActivity.class);
            startActivity(intent);
            return true;
        }
        return super.onOptionsItemSelected(item);
    }

    private class CloadImage extends AsyncTask<String, Integer, List<ImageItem>> {
        @Override
        protected List<ImageItem> doInBackground(String... urls) {
            List<ImageItem> itemList = new ArrayList<>();
            HttpURLConnection conn = null;
            try {
                String apiUrl = urls[0];
                URL urlAPI = new URL(apiUrl);
                conn = (HttpURLConnection) urlAPI.openConnection();
                conn.setRequestMethod("GET");
                conn.setConnectTimeout(3000);
                conn.setReadTimeout(3000);
                int responseCode = conn.getResponseCode();
                if (responseCode == HttpURLConnection.HTTP_OK) {
                    InputStream is = conn.getInputStream();
                    BufferedReader reader = new BufferedReader(new InputStreamReader(is));
                    StringBuilder result = new StringBuilder();
                    String line;
                    while ((line = reader.readLine()) != null) {
                        result.append(line);
                    }
                    is.close();
                    String strJson = result.toString();
                    JSONArray aryJson = new JSONArray(strJson);
                    // 각각 게시글에 대해 ImageItem object 생성
                    for (int i = 0; i < aryJson.length(); i++) {
                        post_json = (JSONObject) aryJson.get(i);
                        imageUrl = post_json.optString("image", "");
                        String title = post_json.optString("title", "");
                        String text = post_json.optString("text", "");
                        int id = post_json.optInt("id", -1);
                        if (imageUrl != null && !imageUrl.isEmpty()) {
                            HttpURLConnection imgConn = null;
                            InputStream imgStream = null;
                            try {
                                URL myImageUrl = new URL(imageUrl);
                                imgConn = (HttpURLConnection) myImageUrl.openConnection();
                                imgConn.setConnectTimeout(5000);
                                imgConn.setReadTimeout(5000);
                                imgStream = imgConn.getInputStream();
                                Bitmap imageBitmap = BitmapFactory.decodeStream(imgStream);
                                if (imageBitmap != null) {
                                    itemList.add(new ImageItem(imageBitmap, title, text, imageUrl, id));
                                }
                            } catch (IOException e) {
                                e.printStackTrace();
                            } finally {
                                if (imgStream != null) try { imgStream.close(); } catch (IOException ignored) {}
                                if (imgConn != null) imgConn.disconnect();
                            }
                        }
                    }
                }
            } catch (IOException | JSONException e) {
                e.printStackTrace();
            } finally {
                if (conn != null) conn.disconnect();
            }
            return itemList;
        }

        @Override
        protected void onPostExecute(List<ImageItem> items) {
            if (swipeRefresh != null && swipeRefresh.isRefreshing()) swipeRefresh.setRefreshing(false);
            if (items == null || items.isEmpty()) {
                textView.setText("불러올 이미지가 없습니다.");
            } else {
                textView.setText("이미지 로드 성공!");
                RecyclerView recyclerView = findViewById(R.id.recyclerView);
                ImageAdapter adapter = new ImageAdapter(items);
                recyclerView.setLayoutManager(new LinearLayoutManager(MainActivity.this));
                recyclerView.setAdapter(adapter);
            }
        }
    }
 /*
 private class PutPost extends AsyncTask<String, Void, Void> {
 // PutPost(게시물 수정) 기능은 리스트에서 게시글 클릭할 시 UploadActivity로 이동 후 Activity 재사용하여 처리
 } */
}