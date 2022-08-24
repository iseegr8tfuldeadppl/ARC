package mustshop.arduino.armforarc;

import android.content.Context;
import android.os.Build;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.bumptech.glide.Glide;

import java.util.List;

import mustshop.arduino.armforarc.MainActivity.Coordinate;

public class CoordinateListAdapter extends RecyclerView.Adapter<CoordinateListAdapter.ViewHolder> {


    private LayoutInflater mInflater;
    private List<Coordinate> coordinates;

    static class ViewHolder extends RecyclerView.ViewHolder {
        TextView bottomTitle, bottomAngle, tiltAngle, tiltTitle, spineTitle, spineAngle, mouthTitle, mouthAngle, gateTitle, gateAngle;
        ImageView up, down, play;
        TextView index;
        TextView edit, remove;
        LinearLayout toggleable;
        FrameLayout persistent;

        ViewHolder(View itemView) {
            super(itemView);
            edit = itemView.findViewById(R.id.edit);
            remove = itemView.findViewById(R.id.remove);

            persistent = itemView.findViewById(R.id.persistent);
            toggleable = itemView.findViewById(R.id.toggleable);

            up = itemView.findViewById(R.id.up);
            down = itemView.findViewById(R.id.down);
            play = itemView.findViewById(R.id.play);

            bottomTitle = itemView.findViewById(R.id.bottomTitle);
            bottomAngle = itemView.findViewById(R.id.bottomAngle);
            tiltTitle = itemView.findViewById(R.id.tiltTitle);
            tiltAngle = itemView.findViewById(R.id.tiltAngle);
            spineTitle = itemView.findViewById(R.id.spineTitle);
            spineAngle = itemView.findViewById(R.id.spineAngle);
            mouthTitle = itemView.findViewById(R.id.mouthTitle);
            mouthAngle = itemView.findViewById(R.id.mouthAngle);
            gateTitle = itemView.findViewById(R.id.gateTitle);
            gateAngle = itemView.findViewById(R.id.gateAngle);

            index = itemView.findViewById(R.id.index);
        }
    }

    public CoordinateListAdapter(Context context, List<Coordinate> coordinates) {
        this.coordinates = coordinates;
        this.mInflater = LayoutInflater.from(context);
    }

    @NonNull
    @Override
    public CoordinateListAdapter.ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View contactView = mInflater.inflate(R.layout.coordinate, parent, false);
        return new ViewHolder(contactView);
    }

    @Override
    public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
        int positionReal = holder.getAdapterPosition();
        Coordinate coordinate = coordinates.get(positionReal);
        Context context = holder.itemView.getContext();

        holder.bottomAngle.setText(String.valueOf(coordinate.bottom));
        holder.spineAngle.setText(String.valueOf(coordinate.spine));
        holder.tiltAngle.setText(String.valueOf(coordinate.tilt));
        holder.mouthAngle.setText(String.valueOf(coordinate.mouth));
        holder.gateAngle.setText(String.valueOf(coordinate.gate));

        CoordinateToBePlayedInterface callback = (CoordinateToBePlayedInterface) context;

        holder.index.setText("#" + (coordinates.size()-positionReal));
        if(callback.areWePlaying()){
            if(callback.whichOneBeingPlayedRn()==positionReal){
                applyColor(holder.index, R.color.orange, context);
            } else {
                applyColor(holder.index, R.color.black, context);
            }
        } else {
            applyColor(holder.index, R.color.black, context);
        }

        holder.play.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if(!callback.areWePlaying()) {
                    callback.play(positionReal);
                }
            }
        });

        // togglable menu
        holder.persistent.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if(!callback.areWePlaying()) {
                    if (holder.toggleable.getVisibility() == View.VISIBLE) {
                        //holder.toggleable.setVisibility(View.GONE);
                        callback.notifyToggledMenu(-1);
                    } else {
                        //holder.toggleable.setVisibility(View.VISIBLE);
                        callback.notifyToggledMenu(positionReal);
                    }
                }
            }
        });

        if(callback.whosBeingEdited()==positionReal){
            holder.edit.setVisibility(View.INVISIBLE);
        } else {
            holder.edit.setVisibility(View.VISIBLE);
        }


        if(callback.getCurrentlyOpened()!=positionReal){
            holder.toggleable.setVisibility(View.GONE);
        } else {
            holder.toggleable.setVisibility(View.VISIBLE);

            holder.edit.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {
                    if(!callback.areWePlaying()){
                        callback.setBeingEdited(positionReal);
                        holder.edit.setVisibility(View.INVISIBLE);
                    }
                }
            });

            holder.remove.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {
                    if(!callback.areWePlaying()) {
                        callback.remove(positionReal);
                    }
                }
            });

            // if this item is at the top don't show the arrow up button
            if(positionReal==coordinates.size()-1){
                holder.down.setVisibility(View.INVISIBLE);
            } else {
                holder.down.setVisibility(View.VISIBLE);

                holder.down.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View view) {
                        if(positionReal!=coordinates.size()-1 && !callback.areWePlaying()) {
                            callback.slide(positionReal, -1);
                        }
                    }
                });
            }

            if(positionReal==0){
                holder.up.setVisibility(View.INVISIBLE);
            } else {
                holder.up.setVisibility(View.VISIBLE);

                holder.up.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View view) {
                        if(positionReal!=0 && !callback.areWePlaying()) {
                            callback.slide(positionReal, 1);
                        }
                    }
                });
            }
        }
    }


    private void applyColor(TextView element, int color, Context context){
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M)
            element.setTextColor(context.getColor(color));
        else
            element.setTextColor(context.getResources().getColor(color));
    }

    void glider(Context context, int source, ImageView image){
        try {
            Glide.with(context).load(source).into(image);
        } catch (Exception e) {
            Log.i("HH", e.toString());
            e.printStackTrace();
        }
    }

    private void log(Object log){
        Log.i("HH", String.valueOf(log));
    }

    @Override
    public int getItemCount() { return coordinates.size(); }

}
