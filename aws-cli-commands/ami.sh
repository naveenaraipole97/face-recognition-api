rm -rf /home/ec2-user/app
mkdir -p /home/ec2-user/app/face_recognition_part2
cd /tmp/
git clone https://github.com/naveenaraipole97/face_recognition_part2.git
cp -r face_recognition_part2/model /home/ec2-user/app/face_recognition_part2/