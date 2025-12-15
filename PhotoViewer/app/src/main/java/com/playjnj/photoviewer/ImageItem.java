package com.playjnj.photoviewer;

import android.graphics.Bitmap;

public class ImageItem {
    private final Bitmap bitmap;
    private final String title;
    private final String text;
    private final String imageUrl;
    private final int id;

    public ImageItem(Bitmap bitmap, String title) {
        this(bitmap, title, "", "", -1);
    }

    public ImageItem(Bitmap bitmap, String title, String text, String imageUrl, int id) {
        this.bitmap = bitmap;
        this.title = title;
        this.text = text;
        this.imageUrl = imageUrl;
        this.id = id;
    }

    public Bitmap getBitmap() { return bitmap; }
    public String getTitle() { return title; }
    public String getText() { return text; }
    public String getImageUrl() { return imageUrl; }
    public int getId() { return id; }
}
