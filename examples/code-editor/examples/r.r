# Load required libraries for data manipulation and visualization
library(dplyr)
library(ggplot2)

# Create a sample dataset with random values
data <- data.frame(
  group = rep(c("A", "B", "C"), each = 10),
  value = rnorm(30, mean = 50, sd = 15),
  count = sample(1:100, 30)
)

# Process data using tidyverse pipes and functions
result <- data %>%
  filter(count > 20) %>%
  group_by(group) %>%
  summarise(
    mean_value = mean(value),
    median_count = median(count),
    n = n(),
    .groups = "drop"
  )

# Create visualization with ggplot2
plot_output = ggplot(result, aes(x = group, y = mean_value, fill = group)) +
  geom_col(alpha = 0.8, show.legend = FALSE) +
  labs(title = "Summary Statistics by Group", x = "Group", y = "Mean Value") +
  theme_minimal() +
  theme(plot.title = element_text(hjust = 0.5, size = 14, face = "bold"))

print(plot_output)
