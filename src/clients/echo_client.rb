require 'cocaine'
require 'cocaine/synchrony/service'
require 'em-synchrony'

class EchoClient
  EM.synchrony do
    results = []
    service = Cocaine::Synchrony::Service.new 'echo'
    channel = service.enqueue('ping', 'Hello from Ruby!')
    channel.each do |result|
      results.push result
    end
    puts results
    EM.stop
  end
end