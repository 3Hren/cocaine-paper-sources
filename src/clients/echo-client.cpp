#include <cocaine/framework/services/app.hpp>
#include <cocaine/framework/services/storage.hpp>

#include <iostream>

#include <boost/asio.hpp>

namespace cf = cocaine::framework;

int main(int argc, char** argv) {
    auto manager = cf::service_manager_t::create(cf::service_manager_t::endpoint_t("localhost", 10053));

    // Get application service object.
    auto app = manager->get_service<cf::app_service_t>("echo");

    boost::asio::io_service io_service;
    boost::asio::io_service::work work(io_service);

    int counter = 0;

    // Call application.
    auto g1 = app->enqueue("ping", "Hello from C++");
    auto g2 = app->enqueue("ping", "Hello again!");
    auto handler = [&counter, &io_service](cf::generator<std::string>& g) {
        counter++;

        try {
            // Always packed data.
            std::cout << "result: " << g.next() << std::endl;
        } catch (const std::exception& e) {
            std::cout << "error: " << e.what() << std::endl;
        }

        if (counter == 2) {
            io_service.stop();
        }
    };
    g1.then(handler);
    g2.then(handler);

    io_service.run();
    return 0;
}