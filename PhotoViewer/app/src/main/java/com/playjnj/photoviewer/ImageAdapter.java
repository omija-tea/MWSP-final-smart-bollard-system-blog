package com.playjnj.photoviewer;

import android.content.Intent;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.recyclerview.widget.RecyclerView;

import java.util.List;

public class ImageAdapter extends RecyclerView.Adapter<ImageAdapter.ImageViewHolder> {
    private List<ImageItem> items;

    public ImageAdapter(List<ImageItem> items) {
        this.items = items;
    }

    @Override
    public ImageViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_image, parent, false);
        return new ImageViewHolder(view);
    }

    @Override
    public void onBindViewHolder(ImageViewHolder holder, int position) {
        ImageItem item = items.get(position);
        holder.imageView.setImageBitmap(item.getBitmap());
        holder.titleText.setText(item.getTitle());

        // 게시글이 클릭되면 edit 화면으로 넘겨주기
        holder.itemView.setOnClickListener(v -> {
            Intent intent = new Intent(v.getContext(), UploadActivity.class);
            intent.putExtra("post_id", item.getId());
            intent.putExtra("title", item.getTitle());
            intent.putExtra("text", item.getText());
            intent.putExtra("image_url", item.getImageUrl());
            v.getContext().startActivity(intent);
        });
    }

    @Override
    public int getItemCount() {
        return items == null ? 0 : items.size();
    }

    public static class ImageViewHolder extends RecyclerView.ViewHolder {
        ImageView imageView;
        TextView titleText;

        public ImageViewHolder(View itemView) {
            super(itemView);
            imageView = itemView.findViewById(R.id.imageViewItem);
            titleText = itemView.findViewById(R.id.titleText);
        }
    }
}