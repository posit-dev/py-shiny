use std::collections::HashMap;
use std::fmt;

/// Represents a user in the system
#[derive(Debug, Clone)]
struct User {
    id: u32,
    name: String,
    email: String,
}

/// Trait for objects that can be validated
trait Validatable {
    fn validate(&self) -> Result<(), String>;
}

impl Validatable for User {
    fn validate(&self) -> Result<(), String> {
        if self.name.is_empty() {
            Err("Name cannot be empty".to_string())
        } else {
            Ok(())
        }
    }
}

/// Generic function to find items in a collection
fn find_user<'a>(users: &'a [User], predicate: impl Fn(&User) -> bool) -> Option<&'a User> {
    users.iter().find(|u| predicate(u))
}

fn main() {
    let mut registry: HashMap<u32, User> = HashMap::new();

    let user = User {
        id: 1,
        name: "Alice".to_string(),
        email: "alice@example.com".to_string(),
    };

    if let Ok(_) = user.validate() {
        registry.insert(user.id, user.clone());
        println!("User {} registered successfully", user.name);
    }

    let users = vec![user];
    match find_user(&users, |u| u.id == 1) {
        Some(found_user) => println!("Found: {:?}", found_user),
        None => println!("User not found"),
    }
}
