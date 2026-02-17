

convert -density 600 input.pdf -background black -gravity center -extent 2100x2970 -quality 100 -gravity northwest +adjoin - | montage - -tile 4x4 -geometry +10+10 output.pdf


magick -density 300 input.pdf -background black -gravity center -extent 2100x2970 -quality 100 -gravity northwest +adjoin temp-%03d.png && montage $(ls temp-*.png | sort -t '-' -k2,2n) -tile 4x4 -geometry +10+10 -output output.pdf



magick -density 300 input.pdf -background black -gravity center -extent 2100x2970 -quality 100 temp-%04d.png && for col in {0..3}; do for row in {0..3}; do idx=$((row * 4 + col + 1)); printf "temp-%04d.png\n" $idx; done; done | xargs montage -tile 4x4 -geometry +10+10 -background black output.pdf




magick -density 300 input.pdf -background black -gravity center -extent 2100x2970 -quality 100 temp-%04d.png && \
for col in {0..3}; do \
    for row in {0..3}; do \
        idx=$((row * 4 + col + 1)); \
        printf "temp-%04d.png\n" $idx; \
    done; \
done | xargs -n16 montage -tile 4x4 -geometry +10+10 -background black montage-output.png && \
magick montage-output.png output.pdf




magick -density 300 input.pdf -background black -gravity center -extent 2100x2970 -quality 100 temp-%04d.png && \
montage temp-*.png -tile 4x4 -geometry +10+10 -background black montage-output.png && \
magick montage-output.png output.pdf && \
rm temp-*.png montage-output.png


magick -density 300 input.pdf -background black -gravity center -extent 2100x2970 -quality 100 temp-%04d.png && \
montage temp-*.png -tile 4x4 -geometry +10+10 -background black miff:- | magick miff:- output.pdf && \
rm temp-*.png




orientation="paysage"; [ "$orientation" = "portrait" ] && final_width=2100 final_height=2970 || final_width=2970 final_height=2100

final_width=2970 && final_height=2100 \
magick -density 300 input.pdf -resize ${final_width}x${final_height}\> -background black -gravity center -extent ${final_width}x${final_height} -quality 100 temp-%04d.png && \
total_pages=$(ls temp-*.png | wc -l) && \
for ((i=0; i<total_pages; i+=16)); do \
  montage $(ls temp-*.png | sed -n "$((i+1)),$((i+16))p") -tile 4x4 -geometry +10+10 -background black page-$((i/16+1)).png; \
done && \
magick page-*.png output.pdf && \
rm temp-*.png page-*.png


final_width=2970 && final_height=2100 && background_color="#181A1B" \
magick -density 300 input.pdf -resize ${final_width}x${final_height}\> -background ${background_color} -gravity center -extent ${final_width}x${final_height} -quality 100 temp-%04d.png && \
total_pages=$(ls temp-*.png | wc -l) && \
for ((i=0; i<total_pages; i+=16)); do \
  montage $(ls temp-*.png | sed -n "$((i+1)),$((i+16))p") -tile 4x4 -geometry +10+10 -background ${background_color} page-$((i/16+1)).png; \
done && \
magick page-*.png output.pdf && \
rm temp-*.png page-*.png



final_width=2970 && final_height=2100 && background_color="#181A1B" \
magick -density 300 input.pdf -resize ${final_width}x${final_height}\> -background ${background_color} -gravity center -extent ${final_width}x${final_height} -quality 100 temp-%04d.png && \
total_pages=$(ls temp-*.png | wc -l) && \
for ((i=0; i<total_pages; i+=16)); do \
  montage $(ls temp-*.png | sed -n "$((i+1)),$((i+16))p") -tile 4x4 -geometry +10+10 -background ${background_color} page-$((i/16+1)).png; \
done && \
magick page-*.png output.pdf && \
rm temp-*.png page-*.png



Peux-tu me corriger cette commande pour que les pages soient distribuées de la manière suivante qui est un exemple uniquement pour les 16 premières pages, mais il faut le faire pour tout toutes les pages :
1,5,9 13
2,6,10,14
3,7, 11,15
4,8, 12,16

final_width=2970 && final_height=2100 && background_color="#181A1B" \
magick -density 300 input.pdf -resize ${final_width}x${final_height}\> -background ${background_color} -gravity center -extent ${final_width}x${final_height} -quality 100 temp-%04d.png && \
total_pages=$(ls temp-*.png | wc -l) && \
for ((i=0; i<total_pages; i+=16)); do \
  montage $(ls temp-*.png | sed -n "$((i+1)),$((i+16))p") -tile 4x4 -geometry +10+10 -background ${background_color} page-$((i/16+1)).png; \
done && \
magick page-*.png output.pdf && \
rm temp-*.png page-*.png



final_width=2970 && final_height=2100 && background_color="#181A1B" \
magick -density 300 input.pdf -resize ${final_width}x${final_height}\> -background ${background_color} -gravity center -extent ${final_width}x${final_height} -quality 100 temp-%04d.png && \
total_pages=$(ls temp-*.png | wc -l) && \
for ((i=0; i<total_pages; i+=16)); do \
  montage $(ls temp-*.png | sed -n "$((i+1)),$((i+16))p") -tile 4x4 -geometry +10+10 -background ${background_color} page-$((i/16+1)).png; \
done && \
magick page-*.png output.pdf && \
rm temp-*.png page-*.png



