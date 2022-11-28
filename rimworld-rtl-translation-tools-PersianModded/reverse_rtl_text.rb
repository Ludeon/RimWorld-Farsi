#! /usr/bin/env ruby
require 'nokogiri'

### Methods
def parse_directory(directory_path)
  Dir["#{directory_path.chomp('/')}/**/*.xml"].each { |file_path| parse_file(file_path) }
end

def parse_file(file_path)
  return puts "[WARN] #{file_path} is not an XML file; skipping." unless file_path.match(/\.xml$/)

  doc = File.open(file_path) { |file| Nokogiri::XML(file) }

  # Valid translation files have specific root nodes
  return puts "[WARN] #{file_path} contains no expected nodes; skipping." if doc.xpath('//LanguageInfo', '//LanguageData').length <= 0

  # Search all leaf nodes since that's where all the translation strings are
  doc.xpath('//*[not(*)]').each do |node|
    node = reverse_node(node)
  end

  File.write(file_path, doc.to_xml)
  puts "[INFO] #{file_path} parsed and strings reversed!"
end

def reverse_node(node)
  if node.content.match(/(\p{Arabic})|(\p{Hebrew})/) then
    words = node.content.split
    words.each do |word|
      # If there are any placeholders (e.g. {0}, {PAWN_FIRST_NAME}) in the word,
      # we wanna preserve that as-is. So, we'll build a list of placeholders
      # and their index in the word ( e.g. [["{0}", 2], ["{PAWN}", 5]])...
      placeholders = []
      word.scan(/{.*?}/) { |match| placeholders << [match, $~.offset(0)[0]] }
      placeholders.each { |placeholder| word.sub!(placeholder[0], '') } if placeholders

      word.reverse! if word.match(/(\p{Arabic})|(\p{Hebrew})/)

      # ...then use it to put the placeholders back in place after we reverse the word
      placeholders.each { |placeholder| word.insert(placeholder[1], placeholder[0]) } if placeholders
    end
    words.reverse!

    node.content = words.join(' ')
    return node
  end
end
###

### Run script
if ARGV.length != 1 then
  puts "Usage:"\
       "reverse_rtl_text.rb [file-path|directory-path]"
  exit
end

path = ARGV[0]

if File.directory?(path) then
  parse_directory(path)
elsif File.file?(path) then
  parse_file(path)
else
  puts "[EROR] Unknown file or directory path: #{path}"
  exit
end
