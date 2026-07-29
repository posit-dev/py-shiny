#include <iostream>
#include <vector>
#include <algorithm>
#include <memory>

namespace DataProcessing {
  // Template function for processing collections
  template <typename T>
  class DataProcessor {
  private:
    std::vector<T> data;

  public:
    DataProcessor(const std::vector<T>& input) : data(input) {}

    // Process data with lambda and range-based for
    auto transform(auto&& func) const {
      std::vector<decltype(func(data[0]))> result;
      for (const auto& item : data) {
        result.push_back(func(item));
      }
      return result;
    }

    // Use auto, references, and modern syntax
    auto average() const -> double {
      if (data.empty()) return 0.0;
      double sum = 0;
      for (const auto& val : data) sum += val;
      return sum / data.size();
    }
  };
}
