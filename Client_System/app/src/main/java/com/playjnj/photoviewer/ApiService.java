package com.playjnj.photoviewer;

import okhttp3.MultipartBody;
import okhttp3.RequestBody;
import okhttp3.ResponseBody;
import retrofit2.Call;
import retrofit2.http.DELETE;
import retrofit2.http.Header;
import retrofit2.http.Multipart;
import retrofit2.http.POST;
import retrofit2.http.Part;
import retrofit2.http.PATCH;
import retrofit2.http.Path;

public interface ApiService {
    @Multipart
    @POST("Post/")
    Call<ResponseBody> createPost(
            @Header("Authorization") String auth,
            @Part("title") RequestBody title,
            @Part("text") RequestBody text,
            @Part MultipartBody.Part image
    );

    @Multipart
    @PATCH("Post/{id}/")
    Call<ResponseBody> updatePost(
            @Header("Authorization") String auth,
            @Path("id") int id,
            @Part("title") RequestBody title,
            @Part("text") RequestBody text,
            @Part MultipartBody.Part image
    );

    @DELETE("Post/{id}/")
    Call<ResponseBody> deletePost(
            @Header("Authorization") String auth,
            @Path("id") int id
    );
}
