function showCourseField() {
    var roleSelect = document.getElementById("id_role");
    var courseField = document.getElementById("course_ptr_id");  // Змінив ідентифікатор поля курсу

    if (roleSelect.value === "student") {
        courseField.style.display = "block";  // Показуємо поле курсу
    } else {
        courseField.style.display = "none";  // Приховуємо поле курсу
    }
}