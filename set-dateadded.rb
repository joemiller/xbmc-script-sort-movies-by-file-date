#!/usr/bin/env ruby
#
# Update the new 'dateAdded' field in the database for each file listed
# in the `files` table using the mtime from the file.
#
# Tested with XBMC 12.0 (Frodo) Alpha 6 (September monthly). Database version:
# myvideos68. Should work with earlier versions as long as `dateAdded` column
# exists on the `files` table.
#
# Should be easy to modify to work with SQLite
#
# Joe Miller, <https://github.com/joemiller>

require 'time'
require 'mysql'

mysql_host = 'server1'
mysql_user = 'xbmc'
mysql_pass = 'xbmc'
mysql_db   = 'myvideos68'

videos_dir = '/Volumes/TV_Shows'

m = Mysql::new(mysql_host, mysql_user, mysql_pass, mysql_db)

Dir.glob("#{videos_dir}/**/*.mkv").each do |file|
  basename = File.basename(file)
  mtime = File.stat(file).mtime
  res = m.query("SELECT idFile FROM files WHERE strFilename = '#{Mysql.escape_string(basename)}'")
  if res.num_rows > 0
    id = res.fetch_row[0]
    time_str = mtime.strftime('%Y-%m-%d %H:%M:%S')
    puts "Updating '#{basename}' (idFile: #{id}) dateAdded: #{time_str}"
    m.query("UPDATE files SET dateAdded='#{time_str}' WHERE idFile=#{id}")
  else
    puts "SKIP: Could not find '#{basename}' in mysql"
  end
end
