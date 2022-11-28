#! /usr/bin/env ruby
require 'nokogiri'
# use https://en.wikipedia.org/wiki/Persian_alphabet
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
    node = contexualize_letters(node)
  end

  File.write(file_path, doc.to_xml)
  puts "[INFO] #{file_path} parsed and strings reversed!"
end

# Arabic is cursive by default, and its letters connect (or don't) according to certain rules.
# However, Unity's text renderer does not handle the letters correctly and doesn't display the
# correct context (e.g. a letter should end with a stem to connect to the next letter, etc).
# This method goes through all Arabic letters in the words in the XML node
# and contextualizes them using the Unicode tables so they connect correctly.
def contexualize_letters(node)
  if node.content.match(/(\p{Arabic})|(\p{Hebrew})/) then
    words = node.content.split
    words = words.map { |word|
      word.chars.each_with_index.map { |letter, idx|
        # Letters in the word are already reversed so they'd display properly in-game,
        # so the next letter is actually the previous one, and vice versa
        prev_letter = (idx < word.length - 1 ? word[idx + 1] : nil)
        next_letter = (idx > 0 ? word[idx - 1] : nil)
        letters = contextualize_letter(letter, prev_letter, next_letter)
      }.join
    }

    node.content = words.join(' ')
    return node
  end
end

@letter_was_combined = false
@combining_alef = ''
def contextualize_letter(letter, prev_letter, next_letter)
  # Letter might've been combined as part of the lam-alef combo. If so ignore it to prevent duplicates
  if @letter_was_combined then
    @letter_was_combined = false
    return create_lam_alef_combo(prev_letter, @combining_alef)
  end
  # Combine letters if a lam-alef is detected
  if is_alef?(letter) && !prev_letter.nil? && is_lam?(prev_letter)
    @letter_was_combined = true
    @combining_alef = letter
    return nil
  end

  return letter if is_isolated_letter?(letter)
  letter_code = contextual_connecting_letter(letter, prev_letter, next_letter) if is_connecting_letter?(letter)
  letter_code = contextual_non_connecting_letter(letter, prev_letter) if is_non_connecting_letter?(letter)

  return letter if letter_code.nil?
  return letter_code
end

def is_connecting_letter?(letter)
  # Letters that connect to ones after them
  return 'بپتثجچحخسشصضطظعغفقکگلمنهيی'.include?(letter)
end

def is_non_connecting_letter?(letter)
  # Letters that do not connect to ones after them
  return 'اأإآدذرزژوؤةى'.include?(letter)
end

def is_isolated_letter?(letter)
  # Letters that do not connect to any others (specifically hamza)
  return letter == 'ء'
end

def is_lam?(letter)
  return letter == 'ل'
end
def is_alef?(letter)
  return 'اأإآ'.include?(letter)
end

def create_lam_alef_combo(prev_letter, next_letter)
  letter_map = { # Maps the appropriate lam-alef character based on what kind of alef it is
    'آ' => 0xFEF5,
    'أ' => 0xFEF7,
    'إ' => 0xFEF9,
    'ا' => 0xFEFB
  }
  combo_code = letter_map[next_letter]
  unless prev_letter.nil? || is_non_connecting_letter?(prev_letter) || is_isolated_letter?(prev_letter) || prev_letter.match(/[{}]/)
    combo_code += 0x1
  end
  return [combo_code].pack('U')
end

def contextual_connecting_letter(letter, prev_letter, next_letter)
  contextual_letter = letter_map(letter)
  prev_letter = nil if prev_letter =~ /[{}]/
  next_letter = nil if next_letter =~ /[{}]/

  if next_letter.nil? then
    if prev_letter.nil? || is_non_connecting_letter?(prev_letter) || is_isolated_letter?(prev_letter) then
      return [contextual_letter].pack('U') # isolated form
    else
      return [contextual_letter + 0x1].pack('U') # end form
    end
  end
  if prev_letter.nil? || is_non_connecting_letter?(prev_letter) || is_isolated_letter?(prev_letter) then
    return [contextual_letter + 0x2].pack('U') # beginning form
  end
  return [contextual_letter + 0x3].pack('U') # middle form
end

def contextual_non_connecting_letter(letter, prev_letter)
  contextual_letter = letter_map(letter)

  if prev_letter.nil? || is_non_connecting_letter?(prev_letter) || is_isolated_letter?(prev_letter) then
    return [contextual_letter].pack('U') # isolated form
  end
  return [contextual_letter + 0x1].pack('U') # end form
end

# Map a general unicode to its isolated contextual form code
def letter_map(letter)
  letter_map = {
    'ء' => 0xFE80,
    'آ' => 0xFE81,
    'أ' => 0xFE83,
    'ؤ' => 0xFE85,
    'إ' => 0xFE87,
    'ا' => 0xFE8D,
    'ب' => 0xFE8F,
    'پ' => 0xFB56,
    'ة' => 0xFE93,
    'ت' => 0xFE95,
    'ث' => 0xFE99,
    'ج' => 0xFE9D,
    'چ' => 0xFB7A,
    'ح' => 0xFEA1,
    'خ' => 0xFEA5,
    'د' => 0xFEA9,
    'ذ' => 0xFEAB,
    'ر' => 0xFEAD,
    'ز' => 0xFEAF,
    'ژ' => 0x0698,
    'س' => 0xFEB1,
    'ش' => 0xFEB5,
    'ص' => 0xFEB9,
    'ض' => 0xFEBD,
    'ط' => 0xFEC1,
    'ظ' => 0xFEC5,
    'ع' => 0xFEC9,
    'غ' => 0xFECD,
    'ف' => 0xFED1,
    'ق' => 0xFED5,
    'ک' => 0xFB8E,
    'گ' => 0xFB92,
    'ل' => 0xFEDD,
    'م' => 0xFEE1,
    'ن' => 0xFEE5,
    'ه' => 0xFEE9,
    'و' => 0xFEED,
    'ی' => 0xFBFC,
    'ي' => 0xFEF1,
    'ئ' => 0xFE89
  }

  if letter_map[letter].nil?
    puts "[WARN] Could not find non-connecting letter: #{to_unicode(letter)}"
    return letter
  end
  return letter_map[letter]
end

def to_unicode(text)
  return text.unpack('U*').map{ |i| "\\u" + i.to_s(16).rjust(4, '0') }.join
end
###

### Run script
if ARGV.length != 1 then
  puts "Usage:"\
       "contextualize_arabic_letters.rb [file-path|directory-path]"
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
