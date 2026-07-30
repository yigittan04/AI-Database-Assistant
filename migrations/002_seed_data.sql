-- Roles
INSERT INTO roles (id, role_name, description)
VALUES
(1, 'Administrator', 'Full access to permitted application tables'),
(2, 'Restricted User', 'Limited read-only access')
ON CONFLICT (id) DO NOTHING;

-- Users
INSERT INTO app_users (id, username, password, role_id)
VALUES
(
    1,
    'Yigit',
    '$argon2id$v=19$m=65536,t=3,p=4$3ny5K8wCN04eefWSdTB03Q$xAxpE/0NKBGbBJgwXciHRg80V2fqLNngCZOralQOZOE',
    1
),
(
    2,
    'Yt',
    '$argon2id$v=19$m=65536,t=3,p=4$isPDoSVtqz7n3ePDLHqTzQ$rxRQHdAnkj07QIy7/DErAT/dVMBQTb3ygK4cWFRvK4c',
    2
)
ON CONFLICT (id) DO NOTHING;